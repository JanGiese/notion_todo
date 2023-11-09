QUERY={
    "filter": {
        "or": [
            {
                "property": "Datum/fix",
                "date": {
                    "is_empty": True
                }
            },
            {
                "property": "Datum/fix",
                "date": {
                    "equals": "2023-11-09"
                }
            }
        ]
    }
}