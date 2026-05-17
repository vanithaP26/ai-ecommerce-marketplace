const Category = require("../models/Category");

const createCategory = async (
  req,
  res
) => {
  try {
    const category =
      await Category.create(req.body);

    res.status(201).json(category);
  } catch (error) {
    res.status(500).json({
      message: error.message,
    });
  }
};

const getCategories = async (
  req,
  res
) => {
  try {
    const categories =
      await Category.find();

    res.json(categories);
  } catch (error) {
    res.status(500).json({
      message: error.message,
    });
  }
};

const deleteCategory = async (
  req,
  res
) => {
  try {
    await Category.findByIdAndDelete(
      req.params.id
    );

    res.json({
      message: "Category Deleted",
    });
  } catch (error) {
    res.status(500).json({
      message: error.message,
    });
  }
};

module.exports = {
  createCategory,
  getCategories,
  deleteCategory,
};