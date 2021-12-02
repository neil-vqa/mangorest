db.createUser(
    {
        user: "userme",
        pwd: "passme",
        roles: [
            {
                role: "readWrite",
                db: "mangorest"
            }
        ]
    }
);

db.createCollection("rocket_engines")
db.createCollection("launch_vehicles")

db.rocketeer.insert(
    { "init": 1 }
)

db.launch_vehicles.insert(
    { "init": 1 }
)