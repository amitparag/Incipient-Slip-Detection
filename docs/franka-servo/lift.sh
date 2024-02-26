./servofranka/build/frankaSavePosition --ip 10.0.0.2 --save ./servofranka/build/start_pos.pos
#./servofranka/build/frankaGripper --ip 10.0.0.2 --open
#./servofranka/build/frankaGripper --ip 10.0.0.2 --home
./servofranka/build/frankaGripper --ip 10.0.0.2 --random 0.0098
./servofranka/build/frankaMoveToPosition --ip 10.0.0.2 --read ./servofranka/build/posB.pos
./servofranka/build/frankaMoveToPosition --ip 10.0.0.2 --read ./servofranka/build/start_pos.pos
#./servofranka/build/frankaGripper --ip 10.0.0.2 --open
