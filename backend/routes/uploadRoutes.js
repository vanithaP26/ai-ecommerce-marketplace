const express = require(
  "express"
);

const multer = require(
  "multer"
);


const {
  CloudinaryStorage,
} = require(
  "multer-storage-cloudinary"
);

const cloudinary = require(
  "../config/cloudinary"
);

const router = express.Router();

const storage =
  new CloudinaryStorage({
    cloudinary,

    params: async (
      req,
      file
    ) => ({
      folder: "ecommerce",
      allowed_formats: [
        "jpg",
        "png",
        "jpeg",
      ],
    }),
  });

const upload = multer({
  storage,
});

router.post(
  "/",
  upload.single("image"),
  (req, res) => {
    res.json({
      imageUrl: req.file.path,
    });
  }
);

module.exports = router;