$SERVER="157.253.205.65"
$PASSWORD="labredesML340"
$NUMCLIENTS=25 
$NUMITER=1 
$TORFILE=250
$USERNAME="root"

foreach ($i in ${NUMCLIENTS}) {
  foreach ($j in ${TORFILE}) {
    foreach ($k in ${NUMITER}) {
      mkdir C:\Users\Fernando\git\Taller4y5InfracomTephaDomain\Bittorrent\Clients_${i}_${k}_${j}\
      for ($l = 1; ${l} -le ${i}; ${l} += 1) {
        pscp -pw ${PASSWORD} ${USERNAME}@${SERVER}:"/root/Taller4y5InfracomTephaDomain/Bittorrent/Clients_${i}_${k}_${j}/client_${l}.log" C:\Users\Fernando\git\Taller4y5InfracomTephaDomain\Bittorrent\Clients_${i}_${k}_${j}\client_${l}.log
      }
    }
  }
}