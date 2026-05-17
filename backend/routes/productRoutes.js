const express = require("express");

const {
  createProduct,
  getProducts,
  getRecommendedProducts,
  deleteProduct,
  getSellerProducts,
  updateProduct,
} = require("../controllers/productController");

const router = express.Router();

router.post("/", createProduct);

router.get("/", getProducts);

router.get("/seller/:sellerId", getSellerProducts);

router.put("/:id", updateProduct);

router.delete("/:id", deleteProduct);

router.get(
  "/recommend/:category",
  getRecommendedProducts
);

module.exports = router;