const Product = require("../models/Product");

const createProduct = async (req, res) => {
  try {
    const product = await Product.create({
      ...req.body,

      seller: req.body.seller,
    });

    res.status(201).json(product);
  } catch (error) {
    res.status(500).json({
      message: error.message,
    });
  }
};

const getProducts = async (req, res) => {
  try {
    const products = await Product.find();

    res.json(products);
  } catch (error) {
    res.status(500).json({
      message: error.message,
    });
  }
};

const getSellerProducts = async (
  req,
  res
) => {
  try {
    const products =
      await Product.find({
        seller: req.params.sellerId,
      });

    res.json(products);
  } catch (error) {
    res.status(500).json({
      message: error.message,
    });
  }
};

const deleteProduct = async (
  req,
  res
) => {
  try {
    await Product.findByIdAndDelete(
      req.params.id
    );

    res.json({
      message: "Product Deleted",
    });
  } catch (error) {
    res.status(500).json({
      message: error.message,
    });
  }
};

const updateProduct = async (
  req,
  res
) => {
  try {
    const product =
      await Product.findById(
        req.params.id
      );

    if (!product) {
      return res.status(404).json({
        message: "Product not found",
      });
    }

    product.title =
      req.body.title ||
      product.title;

    product.description =
      req.body.description ||
      product.description;

    product.price =
      req.body.price ||
      product.price;

    product.category =
      req.body.category ||
      product.category;

    product.stock =
      req.body.stock ||
      product.stock;

    product.image =
      req.body.image ||
      product.image;

    const updatedProduct =
      await product.save();

    res.json(updatedProduct);
  } catch (error) {
    res.status(500).json({
      message: error.message,
    });
  }
};

const getRecommendedProducts = async (
  req,
  res
) => {
  try {
    const { category } = req.params;

    const products = await Product.find({
      category,
    }).limit(4);

    res.json(products);
  } catch (error) {
    res.status(500).json({
      message: error.message,
    });
  }
};

module.exports = {
  createProduct,
  getProducts,
  getRecommendedProducts,
  deleteProduct,
  updateProduct,
  getSellerProducts,
};