import { useEffect, useState } from "react";

import API from "../services/api";

import AdminSidebar from "../components/AdminSidebar";

function AdminProducts() {
  const [products, setProducts] =
    useState([]);

  const fetchProducts =
    async () => {
      const res = await API.get(
        "/products"
      );

      setProducts(res.data);
    };

  useEffect(() => {
    fetchProducts();
  }, []);

  const deleteProduct = async (
    id
  ) => {
    await API.delete(
      `/products/${id}`
    );

    fetchProducts();
  };

  return (
    <div className="flex">
      <AdminSidebar />

      <div className="flex-1 p-10 bg-gray-100 min-h-screen">
        <h1 className="text-4xl font-bold mb-10">
          Products
        </h1>

        <div className="grid md:grid-cols-3 gap-8">
          {products.map((product) => (
            <div
              key={product._id}
              className="bg-white p-6 rounded-xl shadow"
            >
              <img
                src={product.image}
                alt={product.title}
                className="h-56 w-full object-cover rounded-lg"
              />

              <h2 className="text-2xl font-bold mt-4">
                {product.title}
              </h2>

              <p className="text-blue-600 text-xl mt-2">
                ₹{product.price}
              </p>

              <p className="mt-2 text-gray-600">
                {product.category}
              </p>

              <button
                onClick={() =>
                  deleteProduct(product._id)
                }
                className="mt-5 bg-red-500 text-white px-5 py-2 rounded-lg"
              >
                Delete Product
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AdminProducts;