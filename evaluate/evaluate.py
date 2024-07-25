import json
import os

import click
from prettytable import PrettyTable

from moral_keeper_ai import Criteria, MoralKeeperAI


def get_test_comments(lang):
    # 指定されたディレクトリが存在するか確認
    evaluate_path = os.path.join('./data/', lang)
    if not os.path.isdir(evaluate_path):
        print(f"Directory does not exist: {lang}")
        return
    # ディレクトリ内の特定のファイルを指定
    file_path = os.path.join(evaluate_path, 'comments.txt')
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
        self.check_result_table_header = (
            ['num', 'comment_category', 'comment', 'OK']
            + Criteria.get_check_point_list()
            + ['OpenAI Filter', 'Others']
        )
        self.check_result_table = []

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
            print(type(self.test_comments))
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

    def register(self, comment: str, ng_reasons: list) -> None:
        expect = self._comment_to_expect(comment)
        comment_category = self._comment_to_category(comment)

        # 中間集計表へcheck結果を登録
        check_result_row = {}
        self.comment_num += 1
        self.comment_count[comment_category] += 1

        # ヘッダーの順序でrow辞書作成
        check_result_row['num'] = self.comment_num
        check_result_row['comment_category'] = comment_category
        check_result_row['comment'] = comment
        for col_name in self.check_result_table_header:
            check_result_row.setdefault(col_name, 0)

        # check True/False 理由集計
        if 0 == len(ng_reasons):
            check_result_row['OK'] = 1
        else:
            for ng_reason in ng_reasons:
                if ng_reason in check_result_row.keys():
                    check_result_row[ng_reason] = 1
                else:
                    check_result_row['Others'] += 1

        # rowをテーブルに追加
        self.check_result_table.append(check_result_row)

        # ログ表示
        print(f"expect:{expect} ", end='')
        # 期待と結果が一致しない場合は赤色、一致する場合は緑色。
        if expect == bool(check_result_row['OK']):
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
        print(f"[{comment}] -> {ng_reasons}")

        # 文字色を戻す。
        print("\033[39m", end='')

    def print_result(self):
        # print("--------集計表---------")
        # check_result_table = PrettyTable(field_names=self.check_result_table_header)
        # for row in self.check_result_table:
        #     check_result_table.add_row(row.values())
        # print(check_result_table, end="\n\n")

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
            + Criteria.get_check_category_list()
            + ['OpenAI Filter', 'Error' 'Others']
        )
        # 表の初期化
        for reason_category in reason_categorys:
            row = {}
            row.setdefault('AI \\ comment', reason_category)
            for col_name in category_analysis_table_header:
                row.setdefault(col_name, 0)
            _category_analysis_table[reason_category] = row

        # 値を登録する。
        for check_result_row in self.check_result_table:
            # 集計表の行から、理由を走査する。
            hit_categorys = set([])
            if check_result_row['OK']:
                _category_analysis_table['OK'][
                    check_result_row['comment_category']
                ] += 1
            else:
                # check NG
                for reason in Criteria.get_check_point_list() + ['OpenAI Filter']:
                    if check_result_row[reason]:
                        # NG理由がヒットしていた場合
                        if reason == 'OpenAI Filter':
                            reason_category = 'OpenAI Filter'
                            hit_categorys.add(reason_category)
                        elif reason == 'Error':
                            reason_category = 'Error'
                            hit_categorys.add(reason_category)
                        else:
                            for reason_category in Criteria.checkpoint_to_category(
                                reason
                            ):
                                # 同一カテゴリ内の複数理由がヒットしても、カテゴリのカウントは+1にする。
                                hit_categorys.add(reason_category)
                for hited_category in list(hit_categorys):
                    _category_analysis_table[hited_category][
                        check_result_row['comment_category']
                    ] += 1

                if others := check_result_row['Others']:
                    _category_analysis_table['Others'][
                        check_result_row['comment_category']
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
        checkpoints = Criteria.get_check_point_list() + ['Others']

        # 表の初期化
        for checkpoint in checkpoints:
            row = {}
            row.setdefault('prompt', checkpoint)
            for category in Criteria.checkpoint_to_category(checkpoint):
                if checkpoint == 'Others':
                    category = 'others'
                row.setdefault('category', category)
            for col_name in checkpoint_analysis_table_header:
                row.setdefault(col_name, 0)
            _checkpoint_analysis_table[checkpoint] = row

        # 値を登録する。
        for check_result_row in self.check_result_table:
            # 集計表の行から、理由を走査する。
            if check_result_row['OK']:
                pass
            else:
                # check NG
                for reason in Criteria.get_check_point_list():
                    if check_result_row[reason]:
                        _checkpoint_analysis_table[reason][
                            check_result_row['comment_category']
                        ] += 1

                if others := check_result_row['Others']:
                    _checkpoint_analysis_table['Others'][
                        check_result_row['comment_category']
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
    ai = MoralKeeperAI()
    analyst = ai_check_analysis(lang)

    for categorys in test_data_list.values():
        for comments in categorys.values():
            for comment in comments:
                judgement, ng_reasons = ai.check(
                    comment, repeat_check=3, async_mode=False
                )
                analyst.register(comment=comment, ng_reasons=ng_reasons)

    analyst.print_result()


if __name__ == '__main__':
    main()
