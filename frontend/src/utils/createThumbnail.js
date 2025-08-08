import sharp from 'sharp'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const IMAGES_DIR = path.join(__dirname, '../assets/cerfs')
const THUMBS_DIR = path.join(IMAGES_DIR, 'thumbs')

if (!fs.existsSync(THUMBS_DIR)) {
  fs.mkdirSync(THUMBS_DIR)
}

async function createThumbnail(filename, width = 300, height = 300) {
  try {
    const inputPath = path.join(IMAGES_DIR, filename)
    const outputPath = path.join(THUMBS_DIR, filename)

    await sharp(inputPath)
      .resize(width, height, {
        fit: sharp.fit.inside,
        withoutEnlargement: true,
      })
      .toFile(outputPath)

    console.log(`Thumbnail created for ${filename}`)
    return true
  } catch (err) {
    console.error(`Error processing ${filename}:`, err)
    return false
  }
}

async function processAllImages() {
  const files = fs.readdirSync(IMAGES_DIR)

  for (const file of files) {
    if (file === 'thumbs' || fs.statSync(path.join(IMAGES_DIR, file)).isDirectory()) {
      continue
    }

    if (fs.existsSync(path.join(THUMBS_DIR, file))) {
      continue
    }

    await createThumbnail(file)
  }
}

processAllImages().catch(console.error)
