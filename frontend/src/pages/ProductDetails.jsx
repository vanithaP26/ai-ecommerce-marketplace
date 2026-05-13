import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import API from "../services/api";
import ProductCard from "../components/ProductCard";

function ProductDetails() {
  const { id } = useParams();

  const [product, setProduct] = useState(null);

  const [recommended, setRecommended] =
    useState([]);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const res = await API.get("/products");

        const singleProduct = res.data.find(
          (item) => item._id === id
        );

        setProduct(singleProduct);

        if (singleProduct?.category) {
          const recRes = await API.get(
            `/products/recommend/${singleProduct.category}`
          );

          setRecommended(recRes.data);
        }
      } catch (error) {
        console.log(error);
      }
    };

    fetchProduct();
  }, [id]);

  const addToCart = () => {
    let cart =
      JSON.parse(localStorage.getItem("cart")) || [];

    const existingProduct = cart.find(
      (item) => item._id === product._id
    );

    if (existingProduct) {
      existingProduct.quantity += 1;
    } else {
      cart.push({
        ...product,
        quantity: 1,
      });
    }

    localStorage.setItem(
      "cart",
      JSON.stringify(cart)
    );

    alert("Added to Cart");
  };

  if (!product) {
    return <h1>Loading...</h1>;
  }

  return (
    <div className="p-10">
      <div className="grid md:grid-cols-2 gap-10">
        <img
          src={product.image}
          alt={product.title}
          className="w-full rounded-xl"
        />

        <div>
          <h1 className="text-5xl font-bold">
            {product.title}
          </h1>

          <p className="mt-6 text-gray-600 text-lg">
            {product.description}
          </p>

          <h2 className="text-3xl font-bold text-blue-600 mt-6">
            ₹{product.price}
          </h2>

          <button
            onClick={addToCart}
            className="mt-8 bg-black text-white px-8 py-4 rounded-lg"
          >
            Add To Cart
          </button>
        </div>
      </div>

      <div className="mt-20">
        <h2 className="text-4xl font-bold mb-10">
          AI Recommended Products
        </h2>

        <div className="grid md:grid-cols-4 gap-6">
          {recommended.map((item) => (
            <ProductCard
              key={item._id}
              id={item._id}
              title={item.title}
              price={item.price}
              image={item.image}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default ProductDetails;