const express = require("express");

const {
  createProduct,
  getProducts,
  getRecommendedProducts,
} = require("../controllers/productController");

const router = express.Router();

router.post("/", createProduct);

router.get("/", getProducts);

router.get(
  "/recommend/:category",
  getRecommendedProducts
);

module.exports = router;