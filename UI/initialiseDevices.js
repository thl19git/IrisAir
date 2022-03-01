var sqlite3 = require('sqlite3');

const devices = ["0000000085f8eece", "00000000c05cc874", "00000000b21c9dbb", "0000000003c87096"]; 

let db = new sqlite3.Database('database.db', (err) => {
  if(err){
    console.log("Failed to connect to database");
  } else {
    console.log('Connected to the database');
  }
});

db.run('INSERT INTO devices(id) VALUES(?),(?),(?),(?)', devices, (err) => {
  if(err){
    console.log(err);
  } else {
    console.log("Initialised devices");
  }
});

db.close();