const express = require('express');
const cookieParser = require('cookie-parser');
const path = require('path');
const hbs = require('hbs');
const crypto = require('crypto');
const bodyParser = require('body-parser');
var sqlite3 = require('sqlite3');
const { json } = require('body-parser');
const fetch = require('node-fetch');
const base36 = require('base36');

// Define the API address
const apiAddr = "http://3.145.141.152:8000";

// Create the server
var app = express();

// Use the handlebars view engine
app.set('views', path.join(__dirname, "/views"));
app.set('view engine', 'hbs');

// Set up cookies and sessions
app.use(cookieParser());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

// Connect to database
let db = new sqlite3.Database('database.db', (err) => {
  if(err){
    console.log("Failed to connect to database");
  } else {
    console.log('Connected to the database');
  }
});

// Given a password and salt, return the hashed version
const getHashedPassword = (password, salt) => {
  const sha256 = crypto.createHash('sha256');
  const hash = sha256.update(password+salt).digest('base64');
  return hash;
}

// Generates 64 bytes of salt
const generateSalt = () => {
  return crypto.randomBytes(64).toString('hex');
}

// Generates an authentication token
const generateAuthToken = () => {
  return crypto.randomBytes(32).toString('hex');
}

// Helper for parsing dates
const toTimestamp = (strDate) => {
  return Date.parse(strDate);
}

// Encrypts device serial number (returns a string)
const encryptCode = (code) => {
  var temp = base36.base36decode(code);
  temp = String(temp);
  var code = "";
  for (let i = 0; i < temp.length; i++){
    var l = parseInt(temp[i]);
    l += 6;
    l = l % 10;
    code += String(l);
  }
  return code;
}

// Middleware to add user to a request
app.use((req, res, next) => {
  const authToken = req.cookies['AuthToken'];
  db.get('SELECT email FROM auth WHERE token = ?', [authToken], (err, row) => {
    if (err) {
      console.log("Failed to find auth token");
      next();
    }
    if (row) {
      req.user=row.email;
    }
    next();
  });
});


// Set up HTTP request listeners
app.get('/', (req, res) => {
  console.log("Request to /");
  if (req.user) {
    res.render('home');
  } else {
    res.render('index');
  }
});

app.get('/data', (req, res) => {
  console.log("Request to /data");
  //check if logged in
  if (req.user) {
    res.render('data');
  } else {
    res.redirect('/login');
  }
});

app.get('/session', (req, res) => {
  console.log("Request to /session");
  if (req.user) {
    res.render('session');
  } else {
    res.redirect('/login');
  }
});

app.get('/login', (req, res) => {
  console.log("Request to /login");
  if (req.user) {
    res.redirect('/');
  } else {
    res.render('login');
  }
});

app.post('/login', (req, res) => {
  const {email, password} = req.body;
  
  db.get('SELECT password, salt FROM users WHERE email = ?', [email], (err, row) => {
    if (err) {
      console.log("Failed to find password");
      res.render('login', {
        message: 'Oops! Something went wrong',
        messageClass: 'alert-danger'
      });
      return;
    } else {
      if (row) {
        const hashedPassword = getHashedPassword(password,row.salt);
        if (row.password === hashedPassword) {
          const authToken = generateAuthToken();
          db.run('INSERT INTO auth(token, email) VALUES(?,?)', [authToken, email], (err) => {
            if(err){
              console.log("Failed to insert auth token 122");
              res.render('login', {
                message: 'Oops! Something went wrong',
                messageClass: 'alert-danger'
              });
              return;
            }
          });
          res.cookie('AuthToken', authToken);
          res.redirect('/');
          return;
        }
      }
      res.render('login', {
          message: 'Invalid email or password',
          messageClass: 'alert-danger'
      });
    }
  });
});

app.get('/register', (req, res) => {
  console.log("Request to /register");
  res.render('register')
});

app.post('/register', (req, res) => {
  const {email, firstName, password, confirmPassword} = req.body;
  if (password === confirmPassword) {
    db.get('SELECT * FROM users WHERE email = ?', [email], (err, row) => {
      if (err) console.log("Something went wrong checking if user exists");
      if (row) {
        res.render('register', {
        message: 'User already registered',
        messageClass: 'alert-danger'
        });
        return;
      }
      const salt = generateSalt();
      const hashedPassword = getHashedPassword(password,salt);
      db.run('INSERT INTO users(email, first_name, last_name, password, salt, session) VALUES(?,?,?,?,?,?)', [email, firstName[0], firstName[1], hashedPassword, salt, 0], (err) => {
        if(err) {
          console.log("Failed to create user");
          res.render('register', {
            message: 'Oops! Something went wrong',
            messageClass: 'alert-danger'
          });
          return;
        }
      });
      const authToken = generateAuthToken();
      db.run('INSERT INTO auth(token, email) VALUES(?,?)', [authToken, email], (err) => {
        if(err) {
          console.log("Failed to insert auth token");
          res.render('register', {
            message: 'Oops! Something went wrong',
            messageClass: 'alert-danger'
          });
          return;
        }
      });
      res.cookie('AuthToken', authToken);
      res.redirect('/');
    });
  } else {
    res.render('register', {
      message: 'Passwords do not match',
      messageClass: 'alert-danger'
    });
  }
});

app.get('/logout', (req, res) => {
  console.log("Request to /logout");
  if (req.user) {
    const authToken = req.cookies['AuthToken'];
    db.run('DELETE FROM auth WHERE token = ?', [authToken], (err) => {
      if(err) console.log("Failed to delete auth token");
    });
    res.cookie('AuthToken', 'invalid');
    res.redirect('/');
  } else {
    res.redirect('/');
  }
});

app.get('/getUser', (req, res) => {
  console.log("Request to /getUser");
  db.get('SELECT first_name, last_name, device FROM users WHERE email = ?', [req.user], (err, row) => {
    if (err || !row) {
      console.log("Something went wrong retrieving user");
      res.json({name: "", device: ""});
    } else {
      res.json({name: row.first_name, device: row.device});
    }
  });
});

app.post('/addDevice', (req, res) => {
  console.log("Request to /addDevice")
  const {code} = req.body;
  console.log("Trying to add device: " + code);
  db.get('SELECT email FROM devices WHERE id = ?', [code], (err, row) => {
    if(err) {
      console.log("Issue getting device");
      res.json({device: null});
    } else {
      if(row) {
        if(row.email == null) {
          db.run('UPDATE devices SET email = ? WHERE id = ?', [req.user, code], (err) => {
            if(err) {
              console.log("Issue updating email attached to device");
              res.json({device: null});
            }
            db.run('UPDATE users SET device = ? WHERE email = ?', [code, req.user], (err) => {
              if(err) {
                console.log("Issue adding device to user");
                res.json({device: null});
              }
              res.json({device: code});
            })
          });
        } else {
          res.json({device: null});
        }
      } else {
        res.json({device: null});
      }
    }
  });
});

app.post('/removeDevice', (req, res) => {
  console.log("Request to /removeDevice")
  const {code} = req.body;
  console.log("Trying to remove device: " + code);
  db.get('SELECT session FROM users WHERE email = ?', [req.user], (err, row) => {
    if(err) {
      console.log("Error establishing session status before device removal");
      res.json({success: false});
    } else {
      if(row.session) {
        console.log("Trying to remove device ",code, " whilst session is in progress");
        res.json({success: false});
      } else {
        db.run('UPDATE users SET device = ? WHERE email = ?', [null, req.user], (err) => {
          if(err){
            console.log("Error removing device from user");
            res.json({success: false});
          } else {
            db.run('UPDATE devices SET email = ? WHERE id = ?', [null, code], (err) => {
              if(err){
                console.log("Error removing email from device");
                res.json({success: false});
              } else {
                res.json({success: true});
              }
            });
          }
        });
      }
    }
  })
  
});

app.get('/sessionStatus', (req, res) => {
  console.log("Request to /sessionStatus");
  db.get('SELECT device, session FROM users WHERE email = ?', [req.user], (err, row) => {
    if(err){
      console.log("Error getting device and session status");
      res.json({sessionStarted: false, device: null});
    } else {
      sessionBool = row.session ? true : false; 
      res.json({sessionStarted: sessionBool, device: row.device});
    } 
  });
});

app.get('/startSession', (req, res) => {
  console.log("Request to /startSession");
  db.get('SELECT device FROM users WHERE email = ?', [req.user], (err, row) => {
    if(err || row.device == null){
      res.json({success: false});
    } else {
      fetch(apiAddr+"/session/start?serial_number="+encryptCode(row.device) , {
        method: "POST"
      })
        .then( () => {
          db.run('UPDATE users SET session = ?, alert_id = ?, latest_score = ? WHERE email = ?', [1, 0, null, req.user], (err) => {
            if(err){
              res.json({success: false});
            } else {
              res.json({success: true});
            }
          })
        }, () => {
          res.json({success: false});
        });   
    }
  });
});

app.post('/stopSession', (req, res) => {
  console.log("Request to /stopSession");
  const {score, notes} = req.body;
  db.get('SELECT device FROM users WHERE email = ?', [req.user], (err, row) => {
    if(err || row.device == null){
      res.json({success: false});
    } else {
      fetch(apiAddr+"/session/feeling", {
        method: "POST",
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: JSON.stringify({serial_number: encryptCode(row.device), feeling: score})
      })
        .then( () => {
          fetch(apiAddr+"/session/description", {
            method: "POST",
            headers: {'Content-Type': 'application/json; charset=UTF-8'},
            body: JSON.stringify({serial_number: encryptCode(row.device), description: notes})
          })
            .then( () => {
              fetch(apiAddr+"/session/stop?serial_number="+encryptCode(row.device), {
                method: "POST",
              })
                .then( () => {
                  db.run('UPDATE users SET session = ?, alert_id = ? WHERE email = ?', [0, null, req.user], (err) => {
                    if(err){
                      res.json({success: false});
                      return;
                    } else {
                      res.json({success: true});
                      return;
                    }
                  });
                }, () => {
                  res.json({success: false});
                });
            }, () => {
              res.json({success: false});
            });
        }, () => {
          res.json({success: false});
        });
    }
  });
});

app.get('/getAlerts', (req, res) => {
  console.log("Request to /getAlerts");
  db.get('SELECT device, alert_id, latest_score, session FROM users WHERE email = ?', [req.user], (err, row) => {
    if(err || row.device == null || row.session == 0){
      res.json({alert: false, message: null});
    } else {
      fetch(apiAddr+"/predict?serial_number="+encryptCode(row.device),{method: "POST"})
      .then( (response) => {
        response.json()
        .then((data) => {
          feeling,tempDiff,humidityDiff = data;
          console.log("Predicted feeling: ",feeling);
          if((row.alert_id == 0 || feeling != row.latest_score)&&feeling<6&&feeling>0){
            db.run('UPDATE users SET alert_id = ?, latest_score = ? WHERE email = ?', [row.alert_id+1,feeling, req.user], (err) => {
              if(err){
                res.json({alert: false, message: null});
              } else {
                var message = ""
                if(Math.abs(tempDiff*3)>Math.abs(humidityDiff)){
                  if(tempDiff>0){
                    message = "Predicted feeling score: "+feeling+". We recommend you try opening a window or turn off any heating to reduce the temperature."
                  } else {
                    message = "Predicted feeling score: "+feeling+". We recommend you try closing any windows or turning on the heating to reduce the temperature."
                  }
                } else {
                  if(humidityDiff>0){
                    message = "Predicted feeling score: "+feeling+". We recommend you increase airflow or buy a dehumidifier to reduce the humidity."
                  } else {
                    message = "Predicted feeling score: "+feeling+". We recommend you buy a humidifier to increase the humidity."
                  }
                }
                res.json({alert: true, message: message});
              }
            });
          } else {
            res.json({alert: false, message: null});
          }
        }, () => {
          res.json({alert: false, message: null});
        });
      }, (err) => {
        console.log(err);
        res.json({alert: false, message: null});
      });
    }
  });
});

app.get('/getLatestData', (req, res) => {
  console.log("Request to /getLatestData");
  db.get('SELECT device, session FROM users WHERE email = ?', [req.user], (err, row) => {
    if(err || row.device == null || row.session == 0){
      res.json({success: false, temperature: null, humidity: null, intensity: null, colours: null});
    } else {
      fetch(apiAddr+"/session/data?serial_number="+encryptCode(row.device),{method: "POST"})
      .then( (response) => {
        response.json()
        .then((data) => {
          if(data.length<1){
            res.json({success: false, temperature: null, humidity: null, intensity: null, colours: null});
          } else {
            obj = data[data.length-1];
            temp = obj.temp;
            humidity = obj.humidity;
            intensity = obj.intensity;
            colours = [obj.violet, obj.blue, obj.green, obj.yellow, obj.orange, obj.red];
            max_colour = Math.max(obj.violet, obj.blue, obj.green, obj.yellow, obj.orange, obj.red);
            for(let i = 0; i < 6; i++){
              colours[i] = Math.round(colours[i]*100/max_colour);
            }
            res.json({success: true, temperature: temp, humidity: humidity, intensity: intensity, colours: colours});
          }
        })
      }, () => {
        res.json({success: false, temperature: null, humidity: null, intensity: null, colours: null});
      });
    }
  });
});

app.get('/tempHumidityData', (req, res) => {
  console.log("Request to /tempHumidityData");
  db.get('SELECT device, session FROM users WHERE email = ?', [req.user], (err, row) => {
    if(err || row.device == null || row.session == 0){
      res.json({success: false, temperature: null, humidity: null, mintemp: null, maxtemp: null, minhumidity: null, maxhumidity: null});
    } else {
      fetch(apiAddr+"/session/data?serial_number="+encryptCode(row.device),{method: "POST"})
      .then( (response) => {
        response.json()
        .then((data) => {
          if(data.length < 1){
            res.json({success: false, temperature: null, humidity: null, mintemp: null, maxtemp: null, minhumidity: null, maxhumidity: null});
          } else {
            tempdata = [];
            humiditydata = [];
            mintemp = 100;
            maxtemp = 0;
            minhumidity = 100;
            maxhumidity = 0;
            for(let i = 0; i < data.length; i++){
              mintemp = Math.min(mintemp, data[i].temp);
              maxtemp = Math.max(maxtemp, data[i].temp);
              minhumidity = Math.min(minhumidity, data[i].humidity);
              maxhumidity = Math.max(maxhumidity, data[i].humidity);
              timestamp = toTimestamp(data[i].time_stamp);
              tempdata.push({x: timestamp, y: data[i].temp});
              humiditydata.push({x: timestamp, y: data[i].humidity});
            }
            res.json({success: true, temperature: tempdata, humidity: humiditydata, mintemp: Math.floor(mintemp-1), maxtemp: Math.ceil(maxtemp+1), minhumidity: Math.floor(minhumidity-2), maxhumidity: Math.ceil(maxhumidity+2)});
          }
        })
      }, () => {
        res.json({success: false, temperature: null, humidity: null, mintemp: null, maxtemp: null, minhumidity: null, maxhumidity: null});
      });
    }
  });
});

app.get('/sessionData', (req, res) => {
  console.log("Request to /sessionData");
  db.get('SELECT device, session FROM users WHERE email = ?', [req.user], (err, row) => {
    if(err || row.device == null || row.session == 0){
      res.json({success: false, temperature: null, humidity: null, score: null, mintemp: null, maxtemp: null, minhumidity: null, maxhumidity: null, minscore: null, maxscore: null});
    } else {
      fetch(apiAddr+"/session/extract?serial_number="+encryptCode(row.device),{method: "POST"})
      .then( (response) => {
        response.json()
        .then((data) => {
          if(data.length < 1){
            res.json({success: false, temperature: null, humidity: null, score: null, mintemp: null, maxtemp: null, minhumidity: null, maxhumidity: null, minscore: null, maxscore: null});
          } else {
            tempdata = [];
            humiditydata = [];
            scoredata = [];
            mintemp = 100;
            maxtemp = 0;
            minhumidity = 100;
            maxhumidity = 0;
            minscore = 10;
            maxscore = 0;
            for(let i = 0; i < data.length-1; i++){
              mintemp = Math.min(mintemp, data[i].avg_temp);
              maxtemp = Math.max(maxtemp, data[i].avg_temp);
              minhumidity = Math.min(minhumidity, data[i].avg_humidity);
              maxhumidity = Math.max(maxhumidity, data[i].avg_humidity);
              minscore = Math.min(minscore, data[i].feeling);
              maxscore = Math.max(maxscore, data[i].feeling);
              timestamp = toTimestamp(data[i].start);
              tempdata.push({x: timestamp, y: data[i].avg_temp});
              humiditydata.push({x: timestamp, y: data[i].avg_humidity});
              scoredata.push({x: timestamp, y:data[i].feeling});
            }
            console.log(tempdata);
            console.log(humiditydata);
            console.log(scoredata);
            res.json({success: true, temperature: tempdata, humidity: humiditydata, score: scoredata, mintemp: Math.floor(mintemp-1), maxtemp: Math.ceil(maxtemp+1), minhumidity: Math.floor(minhumidity-2), maxhumidity: Math.ceil(maxhumidity+2), minscore: Math.max(minscore-1,0), maxscore: Math.min(maxscore+1,10)});
          }
        })
      }, () => {
        res.json({success: false, temperature: null, humidity: null, score: null, mintemp: null, maxtemp: null, minhumidity: null, maxhumidity: null, minscore: null, maxscore: null});
      });
    }
  });
});

app.get('/style.css', (req, res) => {
  console.log("Request to /style.css");
  res.sendFile(path.join(__dirname, '/public/style.css'));
});

app.get('/main.js', (req, res) => {
  console.log("Request to /main.js");
  res.sendFile(path.join(__dirname, '/public/main.js'));
});

app.get('/main_lo.js', (req, res) => {
  console.log("Request to /main_lo.js");
  res.sendFile(path.join(__dirname, '/public/main_lo.js'));
});

app.get('/home.js', (req, res) => {
  console.log("Request to /home.js");
  res.sendFile(path.join(__dirname, '/public/home.js'));
});

app.get('/session.js', (req, res) => {
  console.log("Request to /session.js");
  res.sendFile(path.join(__dirname, '/public/session.js'));
});

app.get('/data.js', (req, res) => {
  console.log("Request to /data.js");
  res.sendFile(path.join(__dirname, '/public/data.js'));
});
// End of HTTP listeners

// Listen on port 3000
app.listen(3000, () => {
  console.log("Server started on port 3000");
});