import { useState } from "react";
import API from "../services/api";

function Checkout() {
  const [address, setAddress] = useState("");

  const cart =
    JSON.parse(localStorage.getItem("cart")) || [];

  const user =
    JSON.parse(localStorage.getItem("user")) || {};

  const total = cart.reduce(
    (acc, item) =>
      acc + item.price * (item.quantity || 1),
    0
  );

  const placeOrder = async () => {
    try {
      const orderData = {
        user: user.name || "Guest",
        items: cart,
        totalAmount: total,
        address,
      };

      const res = await API.post(
        "/orders",
        orderData
      );

      alert(res.data.message);

      localStorage.removeItem("cart");

      window.location.href = "/";
    } catch (error) {
      console.log(error);
      alert("Order Failed");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-center">
      <div className="bg-white p-10 rounded-xl shadow-lg w-[500px]">
        <h1 className="text-4xl font-bold mb-8">
          Checkout
        </h1>

        <textarea
          placeholder="Enter Delivery Address"
          className="w-full border p-4 rounded-lg h-40"
          value={address}
          onChange={(e) =>
            setAddress(e.target.value)
          }
        />

        <h2 className="text-3xl font-bold mt-6">
          Total: ₹{total}
        </h2>

        <button
          onClick={placeOrder}
          className="mt-8 w-full bg-black text-white py-4 rounded-lg text-lg"
        >
          Place Order
        </button>
      </div>
    </div>
  );
}

export default Checkout;