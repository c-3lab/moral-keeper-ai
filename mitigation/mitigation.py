import json
import os
from os.path import dirname, join

import click
from dotenv import load_dotenv
from prettytable import PrettyTable

from moral_keeper_ai import Criteria, MoralKeeperAI

dotenv_path = join(dirname(__file__), '../.env.local')
load_dotenv(verbose=True, dotenv_path=dotenv_path)


def get_test_comments(lang):
    # 指定されたディレクトリが存在するか確認
    mitigation_path = os.path.join('./data/', lang)
    if not os.path.isdir(mitigation_path):
        print(f"Directory does not exist: {lang}")
        return
    # ディレクトリ内の特定のファイルを指定
    file_path = os.path.join(mitigation_path, 'comments.txt')
    # ファイルが存在するか確認
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return

    # ファイルを読み込む
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # print(f"File content:\n{content}")
    return json.loads(content)


class ai_check_analysis:
    def __init__(self, lang):
        self.test_comments = get_test_comments(lang)
        self.comment_num = 0

        # 結果集計表
        self.f1_table = {
            "true_positive": 0,
            "true_negative": 0,
            "false_positive": 0,
            "false_negative": 0,
        }

        # 集計用中間テーブル
        self.summary_table_header = (
            ['num', 'comment_category', 'comment', 'OK']
            + Criteria.to_prompts(Criteria.ALL)
            + ['OpenAI Filter', 'Others', 'Error']
        )
        self.summary_table = []

        # 各コメントカテゴリ内のコメント数
        self.comment_count = {}
        for category in self._get_comment_categorys():
            self.comment_count.setdefault(category, 0)

    def _strtobool(self, str: str):
        if str in ["true", "True", "TRUE"]:
            return True
        if str in ["false", "False", "FALSE"]:
            return False
        return None

    def _get_comment_categorys(self):
        comment_categorys = []
        for categorys in self.test_comments.values():
            comment_categorys += categorys.keys()
        return comment_categorys

    def _comment_to_expect(self, comment):
        for expect, categorys in self.test_comments.items():
            for comment_list in categorys.values():
                if comment in comment_list:
                    return self._strtobool(expect)
        return None

    def _comment_to_category(self, comment):
        for categorys in self.test_comments.values():
            for category, comment_list in categorys.items():
                if comment in comment_list:
                    return category
        return None

    def _f1_score(self, true_positive, true_negative, false_positive, false_negative):
        # モデルが正しく予測したパターン→頭にT(True)がつく
        # 1 TP(True Positive)：モデルが陽性と予測し、実際も陽性だった
        # 2 TN(Ture Negative)：モデルが陰性と予測し、実際も陰性だった

        # モデルが間違って予測したパターン→頭にF(False)がつく
        # 3 FP(False Positive)：モデルが陽性と予測し、実際は陰性だった
        # 4 FN(False Negative)：モデルが陰性と予測し、実際は陽性だった

        accuracy = (true_positive + true_negative) / (
            true_positive + true_negative + false_positive + false_negative
        )
        print(f"正解率:{accuracy *100} %")

        precision = (true_negative) / (false_positive + true_negative)
        print(f"適合率:{precision*100} % (false 適合率)")

        recall = (true_negative) / (false_negative + true_negative)
        print(f"再現率:{recall*100} % (false 再現率)")

        f1_score = 2 * (precision * recall) / (precision + recall)
        print(f"調和平均:{f1_score*100} %")

    def register(
        self, comment: str, judgment: bool, ng_reasons: list, mitigation_comment
    ) -> None:
        expect = self._comment_to_expect(comment)
        comment_category = self._comment_to_category(comment)

        # 中間集計表に新規追加するrow辞書の初期化
        summary_row = {}
        summary_row['num'] = self.comment_num
        summary_row['comment_category'] = comment_category
        summary_row['comment'] = comment
        for col_name in self.summary_table_header:
            summary_row.setdefault(col_name, 0)

        # ng_reasons 集計
        if judgment:
            if len(ng_reasons) != 0:
                raise Exception
            summary_row['OK'] = 1
        for ng_reason in ng_reasons:
            if ng_reason in summary_row.keys():
                summary_row[ng_reason] = 1
            else:
                summary_row['Others'] += 1
        if 'RateLimitError' in ng_reasons:
            summary_row['Error'] = 1
        else:
            # コメント総数、カテゴリ別コメント数追加
            self.comment_num += 1
            self.comment_count[comment_category] += 1

        # rowをテーブルに追加
        self.summary_table.append(summary_row)

        # ログ表示
        print(f"expect:{expect} ", end='')
        # 期待と結果が一致しない場合は赤色、一致する場合は緑色。
        if bool(summary_row['Error']):
            # Errorは集計対象外
            pass
        elif expect == judgment:
            if expect is True:
                self.f1_table['true_positive'] += 1
            else:
                self.f1_table['true_negative'] += 1
            print("\033[32m", end='')  # 緑
        else:
            if expect is True:
                self.f1_table['false_positive'] += 1
            else:
                self.f1_table['false_negative'] += 1
            print("\033[31m", end='')  # 赤

        # 結果表示
        print(f"[{mitigation_comment}] -> {ng_reasons}")

        # 文字色を戻す。
        print("\033[39m", end='')

    def print_result(self):
        # print("--------集計表---------")
        # summary_table = PrettyTable(field_names=self.summary_table_header)
        # for row in self.summary_table:
        #     summary_table.add_row(row.values())
        # print(summary_table, end="\n\n")

        print(
            "--------各プロンプトカテゴリが、どのコメントカテゴリでNGを出したか---------"
        )
        # 表の主キーリストとカラム名リストを作る
        _category_analysis_table = {}
        category_analysis_table_header = [
            'AI \\ comment'
        ] + self._get_comment_categorys()
        reason_categorys = (
            ['OK']
            + [Criteria.to_str(criteria) for criteria in Criteria.MAPPINGS.keys()]
            + ['OpenAI Filter', 'Error', 'Others']
        )
        # 表の初期化
        for reason_category in reason_categorys:
            row = {}
            row.setdefault('AI \\ comment', reason_category)
            for col_name in category_analysis_table_header:
                row.setdefault(col_name, 0)
            _category_analysis_table[reason_category] = row

        # 値を登録する。
        for summary_row in self.summary_table:
            # 集計表の行から、理由を走査する。
            hit_categorys = set([])
            if summary_row['OK']:
                _category_analysis_table['OK'][summary_row['comment_category']] += 1
            else:
                # check NG
                for reason in Criteria.to_prompts(Criteria.ALL) + ['OpenAI Filter']:
                    if summary_row[reason]:
                        # NG理由がヒットしていた場合
                        if reason == 'OpenAI Filter':
                            reason_category = 'OpenAI Filter'
                            hit_categorys.add(reason_category)
                        elif reason == 'Error':
                            reason_category = 'Error'
                            hit_categorys.add(reason_category)
                        else:
                            hit_categorys.add(
                                *[
                                    Criteria.to_str(criteria)
                                    for criteria in Criteria.MAPPINGS.keys()
                                    if criteria & Criteria.from_prompt(reason)
                                ]
                            )
                for hited_category in list(hit_categorys):
                    _category_analysis_table[hited_category][
                        summary_row['comment_category']
                    ] += 1

                if others := summary_row['Others']:
                    _category_analysis_table['Others'][
                        summary_row['comment_category']
                    ] += others

        # テーブル作成、表示
        category_analysis_table = PrettyTable(
            field_names=category_analysis_table_header
        )
        for row in _category_analysis_table.values():
            # 件数をパーセンテージに変換
            for col_name, value in row.items():
                if comment_count := self.comment_count.get(col_name):
                    row[col_name] = round((value / comment_count) * 100, 1)
            category_analysis_table.add_row(row.values())
        print(category_analysis_table, end="\n\n")

        print("--------各チェック項目が、どのカテゴリのコメントでNGを出したか---------")
        _checkpoint_analysis_table = {}
        checkpoint_analysis_table_header = [
            'prompt',
            'category',
        ] + self._get_comment_categorys()
        checkpoints = Criteria.to_prompts(Criteria.ALL) + ['Others']

        # 表の初期化
        for checkpoint in checkpoints:
            row = {}
            row.setdefault('prompt', checkpoint)
            for category in Criteria.from_prompt(checkpoint):
                if checkpoint == 'Others':
                    category = Criteria.OTHERS
                row.setdefault('category', *[Criteria.to_str(category)])
            for col_name in checkpoint_analysis_table_header:
                row.setdefault(col_name, 0)
            _checkpoint_analysis_table[checkpoint] = row

        # 値を登録する。
        for summary_row in self.summary_table:
            # 集計表の行から、理由を走査する。
            if summary_row['OK']:
                pass
            else:
                # check NG
                for reason in Criteria.to_prompts(Criteria.ALL):
                    if summary_row[reason]:
                        _checkpoint_analysis_table[reason][
                            summary_row['comment_category']
                        ] += 1

                if others := summary_row['Others']:
                    _checkpoint_analysis_table['Others'][
                        summary_row['comment_category']
                    ] += others

        # テーブル作成、表示
        checkpoint_analysis_table = PrettyTable(
            field_names=checkpoint_analysis_table_header
        )
        for row in _checkpoint_analysis_table.values():
            # 件数をパーセンテージに変換
            for col_name, value in row.items():
                if comment_count := self.comment_count.get(col_name):
                    row[col_name] = round((value / comment_count) * 100, 1)
            checkpoint_analysis_table.add_row(row.values())
        print(checkpoint_analysis_table, end="\n\n")

        print(f"{self.f1_table}")
        self._f1_score(**self.f1_table)


@click.command()
@click.argument('lang')
def main(lang):
    test_data_list = get_test_comments(lang)
    # スクリプトのエントリーポイント
    ai = MoralKeeperAI(model='gpt-4o', repeat=1)
    analyst = ai_check_analysis(lang)
    criteria_list = [Criteria.NONE, Criteria.ALL]

    for criteria in criteria_list:
        test_count = 0
        number_true = 0
        if criteria == 0:
            print("現在の設定：Criteria.NONE")
        else:
            print("現在の設定：Criteria.ALL")
        for categorys in test_data_list.values():
            for comments in categorys.values():
                for comment in comments:
                    test_count += 1
                    mitigation_comment = ai.suggest(comment, criteria=criteria)
                    print("緩和前コメント：", comment)
                    judgement, ng_reasons = ai.check(mitigation_comment)
                    if judgement:
                        number_true += 1
                    analyst.register(comment, judgement, ng_reasons, mitigation_comment)

        print(f"緩和表現成功回数：{number_true}/{test_count}")
        analyst.print_result()


if __name__ == '__main__':
    main()
