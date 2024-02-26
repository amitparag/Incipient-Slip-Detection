./servofranka/build/frankaSavePosition --ip 10.0.0.2 --save ./servofranka/build/start_pos.pos

# Grasp object
#./servofranka/build/frankaGripper --ip 10.0.0.2 --open
./servofranka/build/frankaGripper --ip 10.0.0.2 --home
./servofranka/build/frankaGripper --ip 10.0.0.2 --random 0.0035

# Lift object
./servofranka/build/frankaMoveToPosition --ip 10.0.0.2 --read ./servofranka/build/posB.pos

# Shake object
./servofranka/build/frankaShake --ip 10.0.0.2 --read-start ./servofranka/build/posB.pos --read-end ./servofranka/build/rotShake.pos --speed 100 --num-shakes 3
./servofranka/build/frankaShake --ip 10.0.0.2 --read-start ./servofranka/build/posB.pos --read-end ./servofranka/build/vertShake.pos --speed 100 --num-shakes 3
./servofranka/build/frankaShake --ip 10.0.0.2 --read-start ./servofranka/build/posB.pos --read-end ./servofranka/build/perpShake.pos --speed 100 --num-shakes 3
./servofranka/build/frankaShake --ip 10.0.0.2 --read-start ./servofranka/build/posB.pos --read-end ./servofranka/build/tanShake.pos --speed 100 --num-shakes 3

# Put object back
./servofranka/build/frankaMoveToPosition --ip 10.0.0.2 --read ./servofranka/build/start_pos.pos
./servofranka/build/frankaGripper --ip 10.0.0.2 --open