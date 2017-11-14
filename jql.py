

class ProductionSupportFilters(object):

    def __init__(self):
        self.all_issues = "project in (FARM) AND (cf[10614] = 18 OR labels in (totalpkg, prodsup)) ORDER BY Rank ASC"
        self.high_priority_issues = "project in (FARM) AND (cf[10614] = 18 OR labels in (totalpkg, prodsup)) AND (Flagged is not EMPTY OR priority = Blocker) AND sprint in (openSprints(), futureSprints()) ORDER BY Rank ASC"
        self.open_sprints = "project in (FARM, SB, DI, DE) AND (cf[10614] = 18 OR labels in (totalpkg, prodsup)) AND sprint in (openSprints(), futureSprints()) ORDER BY Rank ASC"
