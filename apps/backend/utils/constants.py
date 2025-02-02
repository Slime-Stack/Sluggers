MLB_STATS_API_BASE_URL = "https://statsapi.mlb.com/api/"
MLB_SCHEDULE_API_BASE_URL = f"{MLB_STATS_API_BASE_URL}v1/schedule"
MLB_LOGOS_URL = "https://www.mlbstatic.com/team-logos/"
ISO_FORMAT = "+00:00"
TEAMS = [
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/109.svg",
                    "name": "Arizona Diamondbacks",
                    "shortName": "D-backs",
                    "teamId": 109
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/133.svg",
                    "name": "Athletics",
                    "shortName": "Athletics",
                    "teamId": 133
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/144.svg",
                    "name": "Atlanta Braves",
                    "shortName": "Braves",
                    "teamId": 144
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/110.svg",
                    "name": "Baltimore Orioles",
                    "shortName": "Orioles",
                    "teamId": 110
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/111.svg",
                    "name": "Boston Red Sox",
                    "shortName": "Red Sox",
                    "teamId": 111
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/112.svg",
                    "name": "Chicago Cubs",
                    "shortName": "Cubs",
                    "teamId": 112
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/145.svg",
                    "name": "Chicago White Sox",
                    "shortName": "White Sox",
                    "teamId": 145
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/113.svg",
                    "name": "Cincinnati Reds",
                    "shortName": "Reds",
                    "teamId": 113
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/114.svg",
                    "name": "Cleveland Guardians",
                    "shortName": "Guardians",
                    "teamId": 114
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/115.svg",
                    "name": "Colorado Rockies",
                    "shortName": "Rockies",
                    "teamId": 115
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/116.svg",
                    "name": "Detroit Tigers",
                    "shortName": "Tigers",
                    "teamId": 116
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/117.svg",
                    "name": "Houston Astros",
                    "shortName": "Astros",
                    "teamId": 117
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/118.svg",
                    "name": "Kansas City Royals",
                    "shortName": "Royals",
                    "teamId": 118
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/108.svg",
                    "name": "Los Angeles Angels",
                    "shortName": "Angels",
                    "teamId": 108
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/119.svg",
                    "name": "Los Angeles Dodgers",
                    "shortName": "Dodgers",
                    "teamId": 119
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/146.svg",
                    "name": "Miami Marlins",
                    "shortName": "Marlins",
                    "teamId": 146
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/158.svg",
                    "name": "Milwaukee Brewers",
                    "shortName": "Brewers",
                    "teamId": 158
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/142.svg",
                    "name": "Minnesota Twins",
                    "shortName": "Twins",
                    "teamId": 142
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/121.svg",
                    "name": "New York Mets",
                    "shortName": "Mets",
                    "teamId": 121
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/147.svg",
                    "name": "New York Yankees",
                    "shortName": "Yankees",
                    "teamId": 147
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/143.svg",
                    "name": "Philadelphia Phillies",
                    "shortName": "Phillies",
                    "teamId": 143
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/134.svg",
                    "name": "Pittsburgh Pirates",
                    "shortName": "Pirates",
                    "teamId": 134
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/135.svg",
                    "name": "San Diego Padres",
                    "shortName": "Padres",
                    "teamId": 135
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/137.svg",
                    "name": "San Francisco Giants",
                    "shortName": "Giants",
                    "teamId": 137
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/136.svg",
                    "name": "Seattle Mariners",
                    "shortName": "Mariners",
                    "teamId": 136
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/138.svg",
                    "name": "St. Louis Cardinals",
                    "shortName": "Cardinals",
                    "teamId": 138
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/139.svg",
                    "name": "Tampa Bay Rays",
                    "shortName": "Rays",
                    "teamId": 139
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/140.svg",
                    "name": "Texas Rangers",
                    "shortName": "Rangers",
                    "teamId": 140
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/141.svg",
                    "name": "Toronto Blue Jays",
                    "shortName": "Blue Jays",
                    "teamId": 141
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/120.svg",
                    "name": "Washington Nationals",
                    "shortName": "Nationals",
                    "teamId": 120
                }
            ]
