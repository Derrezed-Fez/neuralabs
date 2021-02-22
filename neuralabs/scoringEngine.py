class ScoringEngine:
    def __init__(self, scoring_type:str, answers:dict, key:list):
        self.scoring_type = scoring_type
        self.answers = answers
        modified_key = dict()
        counter = 1
        for item in key:
            modified_key['page' + str(counter)] = item
        self.key = modified_key

    def calculateScore(self):
        if self.scoring_type == 'comparison':
            return self.comparisonCheck()

    def comparisonCheck(self):
        points = 0
        for key, value in self.answers.items():
            if self.key[key]['hash'] == value:
                points += int(self.key[key]['points'])

        return points
