class Criteria:
    class Gpt35Turbo:
        criteria = [
            'Compliance with company policies',
            'Use appropriate expressions for public communication',
            'The comment contains no personal information',
            (
                'Does not contain personal opinions on religion or politics in the '
                'content or context'
            ),
            'No rumors',
            'Information, if included, must be accurate',
            'Protection of brand image',
            'Does not suggest non-compliance or legal violations',
            'The feedback is not negative',
        ]

    class Gpt4o:
        criteria = [
            'No personal attacks',
            'No discrimination',
            'No threats or violence',
            'No privacy violations',
            'No obscene language',
            'No sexual content',
            'Child-friendly',
            'No harassment',
            'No political promotion',
            'No religious solicitation',
            'Accurate info',
            'No rumors',
            'Correct health info',
            'Protection of brand image',
            'No defamation or unwarranted criticism',
            'Legal compliance and regulations',
            'Adherence to company policies',
        ]

    class Gpt4oMini:
        criteria = [
            'No personal attacks',
            'No discrimination',
            'No threats or violence',
            'No privacy violations',
            'No obscene language',
            'No sexual content',
            'Child-friendly',
            'No harassment',
            'No political promotion',
            'No religious solicitation',
            'Accurate info',
            'No rumors',
            'Correct health info',
            'Protection of brand image',
            'No defamation or unwarranted criticism',
            'Legal compliance and regulations',
            'Adherence to company policies',
        ]
