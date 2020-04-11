https://geth.ethereum.org/docs/interface/private-network

docker-compose --file docker-compose.support.yaml --project-name support run --rm eth geth account new --password /settings/password.txt --datadir /data --lightkdf
put account hash into genesis.json
docker-compose --file docker-compose.support.yaml --project-name support run --rm eth geth init --datadir /data /settings/genesis.json
docker-compose --file docker-compose.support.yaml --project-name support up
docker-compose --file docker-compose.support.yaml --project-name support exec eth geth attach

```javascript
personal.unlockAccount(eth.coinbase, 'admin1234')

personal.sendTransaction({ from: eth.coinbase, to: "0xaf98A2A2f4b2593f21F58A5EA23b54965A3Fe94a", value: web3.toWei(1, "ether") }, 'admin1234')

web3.fromWei(eth.getBalance(eth.coinbase), "ether")

```
0x