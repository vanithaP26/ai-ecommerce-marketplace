const express = require(
  "express"
);

const router =
  express.Router();

const multer = require(
  "multer"
);

const cloudinary = require(
  "../config/cloudinary"
);

const storage =
  multer.memoryStorage();

const upload = multer({
  storage,
});

router.post(
  "/",
  upload.single("image"),

  async (req, res) => {
    try {
      const file =
        req.file.buffer;

      const result =
        await new Promise(
          (resolve, reject) => {
            cloudinary.uploader
              .upload_stream(
                {
                  resource_type:
                    "image",
                },

                (
                  error,
                  result
                ) => {
                  if (error)
                    reject(
                      error
                    );
                  else
                    resolve(
                      result
                    );
                }
              )
              .end(file);
          }
        );

      res.json({
        imageUrl:
          result.secure_url,
      });
    } catch (error) {
      console.log(error);

      res
        .status(500)
        .json({
          message:
            "Upload Failed",
        });
    }
  }
);

module.exports = router;