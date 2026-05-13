import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function Cart() {
  const [cart, setCart] = useState([]);

  useEffect(() => {
    const storedCart =
      JSON.parse(localStorage.getItem("cart")) || [];

    setCart(storedCart);
  }, []);

  const updateCart = (updatedCart) => {
    setCart(updatedCart);

    localStorage.setItem(
      "cart",
      JSON.stringify(updatedCart)
    );
  };

  const increaseQty = (id) => {
    const updatedCart = cart.map((item) =>
      item._id === id
        ? {
            ...item,
            quantity: item.quantity + 1,
          }
        : item
    );

    updateCart(updatedCart);
  };

  const decreaseQty = (id) => {
    const updatedCart = cart
      .map((item) =>
        item._id === id
          ? {
              ...item,
              quantity: item.quantity - 1,
            }
          : item
      )
      .filter((item) => item.quantity > 0);

    updateCart(updatedCart);
  };

  const removeItem = (id) => {
    const updatedCart = cart.filter(
      (item) => item._id !== id
    );

    updateCart(updatedCart);
  };

  const total = cart.reduce(
    (acc, item) =>
      acc + item.price * item.quantity,
    0
  );

  return (
    <div className="p-10 bg-gray-100 min-h-screen">
      <h1 className="text-5xl font-bold mb-10">
        Shopping Cart
      </h1>

      <div className="space-y-6">
        {cart.map((item) => (
          <div
            key={item._id}
            className="bg-white p-6 rounded-xl shadow-lg flex items-center justify-between"
          >
            <div className="flex items-center gap-6">
              <img
                src={item.image}
                alt={item.title}
                className="w-32 h-32 object-cover rounded-lg"
              />

              <div>
                <h2 className="text-2xl font-bold">
                  {item.title}
                </h2>

                <p className="text-blue-600 font-bold mt-2">
                  ₹{item.price}
                </p>

                <button
                  onClick={() =>
                    removeItem(item._id)
                  }
                  className="mt-4 bg-red-500 text-white px-4 py-2 rounded-lg"
                >
                  Remove
                </button>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button
                onClick={() =>
                  decreaseQty(item._id)
                }
                className="bg-gray-300 px-4 py-2 rounded-lg text-xl"
              >
                -
              </button>

              <span className="text-2xl font-bold">
                {item.quantity}
              </span>

              <button
                onClick={() =>
                  increaseQty(item._id)
                }
                className="bg-gray-300 px-4 py-2 rounded-lg text-xl"
              >
                +
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-10 bg-white p-8 rounded-xl shadow-lg">
        <h2 className="text-4xl font-bold">
          Total: ₹{total}
        </h2>

        <Link to="/checkout">
          <button className="mt-6 bg-black text-white px-8 py-4 rounded-lg text-lg">
            Proceed to Checkout
          </button>
        </Link>
      </div>
    </div>
  );
}

export default Cart;