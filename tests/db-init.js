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

db.rocket_engines.insert(
    { "init": 1 }
)

db.launch_vehicles.insert(
    { "init": 1 }
)