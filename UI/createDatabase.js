const fs = require('fs');
var sqlite3 = require('sqlite3');

var db = new sqlite3.Database("database.db");

if(!fs.existsSync("database.db")){

  console.log("creating database file");

  fs.openSync("database.db", "w");

  db.run("CREATE TABLE users (email TEXT NOT NULL PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL, password TEXT NOT NULL, salt TEXT NOT NULL, device TEXT, session INTEGER NOT NULL, alert_id INTEGER, latest_score INTEGER)", function(createResult){
    if(createResult) throw createResult;
  });

  db.run("CREATE TABLE auth (token TEXT NOT NULL PRIMARY KEY, email TEXT NOT NULL, FOREIGN KEY (email) REFERENCES users(email))", function(createResult){
    if(createResult) throw createResult;
  });

  db.run("CREATE TABLE devices (id TEXT NOT NULL PRIMARY KEY, email TEXT , FOREIGN KEY (email) REFERENCES users(email))", function(createResult){
    if(createResult) throw createResult;
  });
  
  console.log("database initialized");
}