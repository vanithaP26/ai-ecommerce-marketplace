import {
  useEffect,
  useState,
} from "react";

import {
  useParams,
  useNavigate,
} from "react-router-dom";

import API from "../services/api";

import Sidebar from "../components/dashboard/Sidebar";

import Topbar from "../components/dashboard/Topbar";

function EditProduct() {
  const { id } = useParams();

  const navigate = useNavigate();

  const [formData, setFormData] =
    useState({
      title: "",
      description: "",
      price: "",
      category: "",
      stock: "",
      image: "",
    });

  const fetchProduct =
    async () => {
      const res = await API.get(
        "/products"
      );

      const product =
        res.data.find(
          (item) => item._id === id
        );

      if (product) {
        setFormData(product);
      }
    };

  useEffect(() => {
    fetchProduct();
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const updateProduct =
    async (e) => {
      e.preventDefault();

      try {
        await API.put(
          `/products/${id}`,
          formData
        );

        alert(
          "Product Updated"
        );

        navigate("/seller");
      } catch (error) {
        alert(
          "Update Failed"
        );
      }
    };

  return (
    <div className="flex bg-gray-100 min-h-screen">

      <Sidebar role="seller" />

      <div className="flex-1 p-8">

        <Topbar title="Edit Product" />

        <div className="bg-white p-8 rounded-2xl shadow">

          <form
            onSubmit={updateProduct}
            className="grid md:grid-cols-2 gap-6"
          >

            <input
              type="text"
              name="title"
              placeholder="Title"
              value={formData.title}
              onChange={handleChange}
              className="border p-4 rounded-xl"
            />

            <input
              type="number"
              name="price"
              placeholder="Price"
              value={formData.price}
              onChange={handleChange}
              className="border p-4 rounded-xl"
            />

            <input
              type="text"
              name="category"
              placeholder="Category"
              value={formData.category}
              onChange={handleChange}
              className="border p-4 rounded-xl"
            />

            <input
              type="number"
              name="stock"
              placeholder="Stock"
              value={formData.stock}
              onChange={handleChange}
              className="border p-4 rounded-xl"
            />

            <input
              type="text"
              name="image"
              placeholder="Image URL"
              value={formData.image}
              onChange={handleChange}
              className="border p-4 rounded-xl md:col-span-2"
            />

            <textarea
              name="description"
              placeholder="Description"
              value={formData.description}
              onChange={handleChange}
              rows="5"
              className="border p-4 rounded-xl md:col-span-2"
            />

            <button className="bg-black text-white py-4 rounded-xl md:col-span-2">
              Update Product
            </button>

          </form>

        </div>

      </div>
    </div>
  );
}

export default EditProduct;