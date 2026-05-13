import { useEffect, useState } from "react";

import API from "../services/api";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function Admin() {
  const [products, setProducts] = useState([]);

  const [orders, setOrders] = useState([]);

  const analyticsData = [
    {
      name: "Products",
      value: products.length,
    },

    {
      name: "Orders",
      value: orders.length,
    },

    {
      name: "Revenue",
      value: orders.reduce(
        (acc, order) =>
          acc + order.totalAmount,
        0
      ),
    },
  ];

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    price: "",
    image: "",
    category: "",
    stock: "",
  });

  const fetchProducts = async () => {
    try {
      const res = await API.get("/products");

      setProducts(res.data);
    } catch (error) {
      console.log(error);
    }
  };

  const fetchOrders = async () => {
    try {
      const res = await API.get("/orders");

      setOrders(res.data);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    fetchProducts();

    fetchOrders();
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const addProduct = async (e) => {
    e.preventDefault();

    try {
      await API.post("/products", formData);

      alert("Product Added");

      fetchProducts();

      setFormData({
        title: "",
        description: "",
        price: "",
        image: "",
        category: "",
        stock: "",
      });
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="p-10 bg-gray-100 min-h-screen">
      <h1 className="text-5xl font-bold mb-10">
        Admin Dashboard
      </h1>

      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-2xl font-bold">
            Products
          </h2>

          <p className="text-4xl mt-4">
            {products.length}
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-2xl font-bold">
            Orders
          </h2>

          <p className="text-4xl mt-4">
            {orders.length}
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-2xl font-bold">
            Revenue
          </h2>

          <p className="text-4xl mt-4">
            ₹
            {orders.reduce(
              (acc, order) =>
                acc + order.totalAmount,
              0
            )}
          </p>
        </div>
      </div>

      <div className="bg-white p-8 rounded-xl shadow-lg mb-12">
        <h2 className="text-3xl font-bold mb-6">
          Add Product
        </h2>

        <form
          onSubmit={addProduct}
          className="grid md:grid-cols-2 gap-6"
        >
          <input
            type="text"
            name="title"
            placeholder="Title"
            value={formData.title}
            onChange={handleChange}
            className="border p-3 rounded-lg"
          />

          <input
            type="text"
            name="price"
            placeholder="Price"
            value={formData.price}
            onChange={handleChange}
            className="border p-3 rounded-lg"
          />

          <input
            type="text"
            name="image"
            placeholder="Image URL"
            value={formData.image}
            onChange={handleChange}
            className="border p-3 rounded-lg"
          />

          <input
            type="text"
            name="category"
            placeholder="Category"
            value={formData.category}
            onChange={handleChange}
            className="border p-3 rounded-lg"
          />

          <input
            type="text"
            name="stock"
            placeholder="Stock"
            value={formData.stock}
            onChange={handleChange}
            className="border p-3 rounded-lg"
          />

          <textarea
            name="description"
            placeholder="Description"
            value={formData.description}
            onChange={handleChange}
            className="border p-3 rounded-lg md:col-span-2"
          />

          <button className="bg-black text-white py-3 rounded-lg md:col-span-2">
            Add Product
          </button>
        </form>
      </div>

      <div className="bg-white p-8 rounded-xl shadow-lg">
        <h2 className="text-3xl font-bold mb-6">
          Recent Orders
        </h2>

        <div className="space-y-6">
          {orders.map((order) => (
            <div
              key={order._id}
              className="border p-4 rounded-lg"
            >
              <h2 className="text-2xl font-bold">
                {order.user}
              </h2>

              <p className="mt-2">
                ₹{order.totalAmount}
              </p>

              <p className="mt-2 text-gray-600">
                {order.address}
              </p>

              <p className="mt-2 text-blue-600">
                {order.status}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white p-8 rounded-xl shadow-lg mt-12">
        <h2 className="text-3xl font-bold mb-6">
          Analytics Dashboard
        </h2>

        <ResponsiveContainer
          width="100%"
          height={400}
        >
          <BarChart data={analyticsData}>
            <XAxis dataKey="name" />

            <YAxis />

            <Tooltip />

            <Bar
              dataKey="value"
              fill="#000"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Admin;