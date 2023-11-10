"""Template for new tasks in Notion."""
TASK_TEMPLATE={
    "parent": {
        "database_id": "0b70c81f5c1d4dd8aa07dd1b59019a80"
    },
    "properties": {
        "Bearbeiter": {
            "id": "Np%5D%7D",
            "type": "multi_select",
            "multi_select": []
        },
        "Status": {
            "status": {
                "name": "Not started"
            }
        },
        "Name": {
            "id": "title",
            "type": "title",
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "Test"
                    }
                }
            ]
        }
    }
}
