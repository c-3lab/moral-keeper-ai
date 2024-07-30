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
            VIOLENT: [],
            INAPPROPRIATE: [
                "Compliance with company policies",
                "Use appropriate expressions for public communication",
                "The comment contains no personal information",
            ],
            SENSITIVE: [
                "Does not contain personal opinions on religion or politics in the "
                "content or context",
            ],
            INACCURATE: [
                "No rumors",
                "Information, if included, must be accurate",
            ],
            DISREPUTE: [
                "Protection of brand image",
                "Does not suggest non-compliance or legal violations",
                "The feedback is not negative",
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

    @staticmethod
    def from_prompt(prompt):
        criteria = 0
        for k, v in Criteria.MAPPINGS.items():
            if prompt in v:
                criteria |= k

        if criteria:
            return Criteria(criteria)
        else:
            return Criteria.OTHERS
