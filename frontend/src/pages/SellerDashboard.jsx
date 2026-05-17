import {
  useEffect,
  useState,
} from "react";

import {
  Package,
  IndianRupee,
  ShoppingCart,
  BarChart3,
} from "lucide-react";

import API from "../services/api";

import Sidebar from "../components/dashboard/Sidebar";

import Topbar from "../components/dashboard/Topbar";

import ChartCard from "../components/dashboard/ChartCard";

import Table from "../components/dashboard/Table";

function SellerDashboard() {
  const user = JSON.parse(
    localStorage.getItem("user")
  );

  const [products, setProducts] =
    useState([]);

  const [formData, setFormData] =
    useState({
      title: "",
      description: "",
      price: "",
      discountPrice: "",
      brand: "",
      image: "",
      category: "",
      stock: "",
      featured: false,
    });

  const fetchProducts =
    async () => {
      try {
        const res = await API.get(
          `/products/seller/${user._id}`
        );

        setProducts(res.data);
      } catch (error) {
        console.log(error);
      }
    };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,

      [e.target.name]:
        e.target.value,
    });
  };

  const uploadImage = async (e) => {
    const file = e.target.files[0];

    const data =
      new FormData();

    data.append(
      "image",
      file
    );

    try {
      const res =
        await API.post(
          "/upload",
          data
        );

      setFormData({
        ...formData,

        image:
          res.data.imageUrl,
      });

      alert(
        "Image Uploaded"
      );
    } catch (error) {
      console.log(error);

      alert(
        "Image Upload Failed"
      );
    }
  };

  const addProduct = async (e) => {
    e.preventDefault();

    try {
      await API.post(
        "/products",
        {
          ...formData,

          seller: user._id,
        }
      );

      alert(
        "Product Added"
      );

      setFormData({
        title: "",
        description: "",
        price: "",
        discountPrice: "",
        brand: "",
        image: "",
        category: "",
        stock: "",
        featured: false,
      });

      fetchProducts();
    } catch (error) {
      console.log(error);

      alert(
        "Failed to add product"
      );
    }
  };

  const deleteProduct =
    async (id) => {
      try {
        await API.delete(
          `/products/${id}`
        );

        fetchProducts();
      } catch (error) {
        console.log(error);
      }
    };

  const totalProducts =
    products.length;

  const totalStock =
    products.reduce(
      (acc, item) =>
        acc +
        Number(item.stock),
      0
    );

  const totalValue =
    products.reduce(
      (acc, item) =>
        acc +
        Number(item.price) *
          Number(item.stock),
      0
    );

  return (
    <div className="flex bg-gray-100 min-h-screen">

      <Sidebar role="seller" />

      <div className="flex-1 p-8">

        <Topbar title="Seller Dashboard" />

        {/* STATS */}

        <div className="grid md:grid-cols-4 gap-6 mb-12">

          <div className="bg-white p-6 rounded-2xl shadow">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-gray-500">
                  Total Products
                </p>

                <h2 className="text-3xl font-bold mt-2">
                  {totalProducts}
                </h2>
              </div>

              <Package size={40} />

            </div>

          </div>

          <div className="bg-white p-6 rounded-2xl shadow">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-gray-500">
                  Inventory
                </p>

                <h2 className="text-3xl font-bold mt-2">
                  {totalStock}
                </h2>
              </div>

              <ShoppingCart size={40} />

            </div>

          </div>

          <div className="bg-white p-6 rounded-2xl shadow">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-gray-500">
                  Store Value
                </p>

                <h2 className="text-3xl font-bold mt-2">
                  ₹{totalValue}
                </h2>
              </div>

              <IndianRupee size={40} />

            </div>

          </div>

          <div className="bg-white p-6 rounded-2xl shadow">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-gray-500">
                  Performance
                </p>

                <h2 className="text-3xl font-bold mt-2">
                  Good
                </h2>
              </div>

              <BarChart3 size={40} />

            </div>

          </div>

        </div>

        {/* ADD PRODUCT */}

        <div className="bg-white p-8 rounded-2xl shadow mb-12">

          <h2 className="text-3xl font-bold mb-8">
            Add New Product
          </h2>

          <form
            onSubmit={addProduct}
            className="grid md:grid-cols-2 gap-6"
          >

            <input
              type="text"
              name="title"
              placeholder="Product Title"
              value={formData.title}
              onChange={
                handleChange
              }
              className="border p-4 rounded-xl"
              required
            />

            <input
              type="number"
              name="price"
              placeholder="Price"
              value={formData.price}
              onChange={
                handleChange
              }
              className="border p-4 rounded-xl"
              required
            />

            <input
              type="number"
              name="discountPrice"
              placeholder="Discount Price"
              value={
                formData.discountPrice
              }
              onChange={
                handleChange
              }
              className="border p-4 rounded-xl"
            />

            <input
              type="text"
              name="brand"
              placeholder="Brand"
              value={formData.brand}
              onChange={
                handleChange
              }
              className="border p-4 rounded-xl"
            />

            <input
              type="text"
              name="category"
              placeholder="Category"
              value={
                formData.category
              }
              onChange={
                handleChange
              }
              className="border p-4 rounded-xl"
              required
            />

            <input
              type="number"
              name="stock"
              placeholder="Stock"
              value={formData.stock}
              onChange={
                handleChange
              }
              className="border p-4 rounded-xl"
              required
            />

            <div className="flex items-center gap-3">

              <input
                type="checkbox"
                name="featured"
                checked={
                  formData.featured
                }
                onChange={(e) =>
                  setFormData({
                    ...formData,

                    featured:
                      e.target
                        .checked,
                  })
                }
              />

              <label>
                Featured Product
              </label>

            </div>

            <input
              type="file"
              onChange={
                uploadImage
              }
              className="border p-4 rounded-xl"
            />

            {/* IMAGE PREVIEW */}

            {formData.image && (

              <div>

                <img
                  src={
                    formData.image
                  }
                  alt="preview"
                  className="w-28 h-28 rounded-xl object-cover border"
                />

              </div>

            )}

            <textarea
              name="description"
              placeholder="Description"
              value={
                formData.description
              }
              onChange={
                handleChange
              }
              className="border p-4 rounded-xl md:col-span-2"
              rows="5"
              required
            />

            <button className="bg-black text-white py-4 rounded-xl text-lg font-semibold md:col-span-2 hover:bg-gray-800 transition">

              Add Product

            </button>

          </form>

        </div>

        {/* CHART */}

        <div className="mb-12">
          <ChartCard />
        </div>

        {/* TABLE */}

        <Table
          products={products}
          deleteProduct={
            deleteProduct
          }
        />

      </div>

    </div>
  );
}

export default SellerDashboard;