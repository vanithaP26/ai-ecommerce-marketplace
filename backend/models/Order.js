const mongoose = require("mongoose");

const orderSchema = new mongoose.Schema(
  {
    user: {
      type: String,
    },

    items: [
      {
        title: String,
        price: Number,
        quantity: Number,
        image: String,
      },
    ],

    totalAmount: {
      type: Number,
    },

    address: {
      type: String,
    },

    status: {
      type: String,
      default: "Pending",
    },
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model(
  "Order",
  orderSchema
);