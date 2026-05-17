import { useEffect, useState } from "react";

import API from "../services/api";

import AdminSidebar from "../components/AdminSidebar";

function AdminCategories() {
  const [categories, setCategories] =
    useState([]);

  const [formData, setFormData] =
    useState({
      name: "",
      image: "",
    });

  const fetchCategories =
    async () => {
      const res = await API.get(
        "/categories"
      );

      setCategories(res.data);
    };

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const addCategory = async (e) => {
    e.preventDefault();

    await API.post(
      "/categories",
      formData
    );

    alert("Category Added");

    setFormData({
      name: "",
      image: "",
    });

    fetchCategories();
  };

  const deleteCategory = async (
    id
  ) => {
    await API.delete(
      `/categories/${id}`
    );

    fetchCategories();
  };

  return (
    <div className="flex">
      <AdminSidebar />

      <div className="flex-1 p-10 bg-gray-100 min-h-screen">
        <h1 className="text-4xl font-bold mb-10">
          Categories
        </h1>

        <form
          onSubmit={addCategory}
          className="bg-white p-6 rounded-xl shadow mb-10 grid md:grid-cols-2 gap-6"
        >
          <input
            type="text"
            name="name"
            placeholder="Category Name"
            value={formData.name}
            onChange={handleChange}
            className="border p-3 rounded-lg"
            required
          />

          <input
            type="text"
            name="image"
            placeholder="Image URL"
            value={formData.image}
            onChange={handleChange}
            className="border p-3 rounded-lg"
            required
          />

          <button className="bg-black text-white py-3 rounded-lg md:col-span-2">
            Add Category
          </button>
        </form>

        <div className="grid md:grid-cols-3 gap-8">
          {categories.map((cat) => (
            <div
              key={cat._id}
              className="bg-white p-6 rounded-xl shadow"
            >
              <img
                src={cat.image}
                alt={cat.name}
                className="h-48 w-full object-cover rounded-lg"
              />

              <h2 className="text-2xl font-bold mt-4">
                {cat.name}
              </h2>

              <button
                onClick={() =>
                  deleteCategory(cat._id)
                }
                className="mt-4 bg-red-500 text-white px-5 py-2 rounded-lg"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AdminCategories;