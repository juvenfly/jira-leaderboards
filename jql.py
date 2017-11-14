

class ProductionSupportFilters(object):

    all_issues = "project in (FARM) AND (cf[10614] = 18 OR labels in (totalpkg, prodsup)) ORDER BY Rank ASC"
    high_priority_issues = "project in (FARM) AND (cf[10614] = 18 OR labels in (totalpkg, prodsup)) AND (Flagged is not EMPTY OR priority = Blocker) AND sprint in (openSprints(), futureSprints()) ORDER BY Rank ASC"
    open_sprints = "project in (FARM, SB, DI, DE) AND (cf[10614] = 18 OR labels in (totalpkg, prodsup)) AND sprint in (openSprints(), futureSprints()) ORDER BY Rank ASC"
