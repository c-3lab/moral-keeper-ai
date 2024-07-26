from enum import IntFlag, auto, nonmember


class Criteria(IntFlag):
    VIOLENT = auto()
    INAPPROPRIATE = auto()
    SENSITIVE = auto()
    INACCURATE = auto()
    DISREPUTE = auto()
    ALL = VIOLENT | INAPPROPRIATE | SENSITIVE | INACCURATE | DISREPUTE
    OTHERS = auto()
    OPENAI_FILTER = auto()

    MAPPINGS = nonmember(
        {
            VIOLENT: [
                "No personal attacks",
                "No discrimination",
                "No threats or violence",
                "No privacy violations",
            ],
            INAPPROPRIATE: [
                "No obscene language",
                "No sexual content",
                "Child-friendly",
                "No harassment",
            ],
            SENSITIVE: [
                "No political promotion",
                "No religious solicitation",
            ],
            INACCURATE: [
                "Accurate info",
                "No rumors",
                "Correct health info",
            ],
            DISREPUTE: [
                "Protection of brand image",
                "No defamation or unwarranted criticism",
                "Legal compliance and regulations",
                "Adherence to company policies",
            ],
        }
    )

    def to_prompts(self) -> list:
        prompts = []
        for k, v in Criteria.MAPPINGS.items():
            if self & k:
                prompts.extend(v)

        return prompts

    @staticmethod
    def to_str(criteria) -> str:
        criteria_to_str = {
            Criteria.VIOLENT: 'violent',
            Criteria.INAPPROPRIATE: 'inappropriate',
            Criteria.SENSITIVE: 'sensitive',
            Criteria.INACCURATE: 'inaccurate',
            Criteria.DISREPUTE: 'disrepute',
            Criteria.OTHERS: 'others',
        }
        return criteria_to_str[criteria]

    def from_prompt(prompt):
        criteria = 0
        for k, v in Criteria.MAPPINGS.items():
            if prompt in v:
                criteria |= k

        if criteria:
            return Criteria(criteria)
        else:
            return Criteria.OTHERS
