const express = require('express')
const app = express()
const multipart = require('connect-multiparty')();
const port = 3000
const process = require('./map')

const outputPath = __dirname + '/public/map'

app.use(express.static('public'))

app.post('/map', multipart, async function (req, res) {
  const { log, map } = req.files
  console.log("Processing: ", [map.path, log.path])
  await process(map.path, log.path, outputPath)
  res.send({ success: true })
})

app.listen(port, '0.0.0.0', () => console.log(`Example app listening 0.0.0.0 on port ${port}!`))