const fs = require('fs')
const { exec: oldExec } = require('child_process');
const { createCanvas, loadImage } = require('canvas')

const SCALE = 2

function exec(cmd) {
  return new Promise((resolve) => {
    oldExec(cmd, resolve)
  })
}

function nextTick() {
  return new Promise((resolve) => {
    setImmediate(resolve)
  })
}

function save(path, canvas) {
  return new Promise((resolve) => {
    const out = fs.createWriteStream(path)
    const stream = canvas.createPNGStream()
    stream.pipe(out)
    out.on('finish', resolve)
  })
}

async function loadCanvas(path) {
  await exec(`convert ${path} /tmp/map.png`)
  const image = await loadImage('/tmp/map.png')
  const canvas = createCanvas(image.width, image.height)
  const ctx = canvas.getContext('2d')
  ctx.drawImage(image, 0, 0)

  return canvas
}

function rotate(srcCanvas, degrees){
  const canvas = createCanvas(srcCanvas.width, srcCanvas.height)
  const context = canvas.getContext('2d')
  context.clearRect(0,0,canvas.width,canvas.height);

  // save the unrotated context of the canvas so we can restore it later
  // the alternative is to untranslate & unrotate after drawing
  context.save();

  // move to the center of the canvas
  // move to the center of the canvas
  context.translate(canvas.width/2,canvas.height/2);

  // rotate the canvas to the specified degrees
  context.rotate((degrees*Math.PI)/180);

  // draw the image
  // since the context is rotated, the image will be rotated also
  context.drawImage(srcCanvas,-srcCanvas.width/2,-srcCanvas.width/2);

  // we’re done with the rotating so restore the unrotated context
  context.restore();

  return canvas
}

async function process(ppmPath, logPath, outputPath) {
  const srcCanvas = await loadCanvas(ppmPath)
  const srcCtx = srcCanvas.getContext('2d')

  let canvas = createCanvas(srcCanvas.width * SCALE, srcCanvas.height * SCALE)
  
  const center = {
    x: canvas.width / 2,
    y: canvas.height / 2,
  }

  let dstCtx = canvas.getContext("2d")

  dstCtx.clearRect(0, 0, canvas.width, canvas.height)

  for (let x = 0; x < srcCanvas.width; x++) {
    const data = srcCtx.getImageData(x, 0, 1, srcCanvas.height).data
    for (let y = 0; y < srcCanvas.height; y++) {
      const r = data[y * 4]
      if (r == 0) {
        dstCtx.fillStyle = 'rgba(255, 255, 255, 0.8)'
        dstCtx.fillRect(x*SCALE, y*SCALE, SCALE, SCALE)
      } else if (r == 255 || r == 78) {
        dstCtx.fillStyle = 'rgba(255, 255, 255, 0.3)'
        dstCtx.fillRect(x*SCALE, y*SCALE, SCALE, SCALE)
      }
    }
    if (x % 1000 == 0) {
      await nextTick()
    }
  }

  canvas = rotate(canvas, 0)
  dstCtx = canvas.getContext("2d")

  const lines = fs.readFileSync(logPath).toString().split('\n');
  const points = []
  for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
    const line = lines[lineIndex];
    if (match = line.match(/estimate (-{0,1}\d+.\d+) (-{0,1}\d+.\d+)/)) {
      const y = center.y - (Math.round((parseFloat(match[2]) * 20)) * SCALE)
      const x = center.x + (Math.round((parseFloat(match[1]) * 20)) * SCALE)

      points.push({ x, y })
    }
  }

  dstCtx.fillStyle = 'rgba(0, 255, 0, 1)'
  dstCtx.fillRect(center.x, center.y, SCALE, SCALE)
  await save(`${outputPath}.grid.png`, canvas)  

  dstCtx.strokeStyle = 'rgb(255, 255, 255)'
  dstCtx.beginPath()
  let waypoint = null
  for (let index = 0; index < points.length; index++) {
    waypoint = points[index]
    const { x, y } = waypoint
    
    if (index == 0) {
      dstCtx.moveTo(x + 0.5, y + 0.5)
    } else {
      dstCtx.lineTo(x + 0.5, y + 0.5)
    }
  }
  dstCtx.stroke()

  dstCtx.fillStyle = 'rgb(0, 255, 0)'
  dstCtx.beginPath();
  dstCtx.arc(center.x, center.y, 3, 0, 2 * Math.PI);
  dstCtx.fill();

  if (waypoint) {
    dstCtx.fillStyle = 'rgb(255, 255, 0)'
    dstCtx.beginPath();
    dstCtx.arc(waypoint.x, waypoint.y, 4, 0, 2 * Math.PI);
    dstCtx.fill();
  }

  await save(`/tmp/full.png`, canvas)

  await exec(`convert -trim /tmp/full.png ${outputPath}.png`) // auto crop
  console.log('The PNG file was created.')
}

module.exports = process