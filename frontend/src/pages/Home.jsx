import { useEffect, useState } from "react";

import Hero from "../components/Hero";
import ProductCard from "../components/ProductCard";

import API from "../services/api";

function Home() {
  const [products, setProducts] = useState([]);

  const [search, setSearch] = useState("");

  const fetchProducts = async () => {
    try {
      const res = await API.get("/products");

      setProducts(res.data);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const filteredProducts = products.filter(
    (product) =>
      product.title
        .toLowerCase()
        .includes(search.toLowerCase())
  );

  return (
    <div>
      <Hero />

      <section className="px-10 py-16 bg-white">
        <h2 className="text-4xl font-bold text-center mb-12">
          Shop By Categories
        </h2>

        <div className="grid md:grid-cols-4 gap-8">
          <div className="bg-black text-white p-10 rounded-2xl text-center text-2xl font-bold hover:scale-105 transition">
            Electronics
        </div>

        <div className="bg-blue-500 text-white p-10 rounded-2xl text-center text-2xl font-bold hover:scale-105 transition">
          Fashion
        </div>

        <div className="bg-green-500 text-white p-10 rounded-2xl text-center text-2xl font-bold hover:scale-105 transition">
          Mobiles
        </div>

        <div className="bg-red-500 text-white p-10 rounded-2xl text-center text-2xl font-bold hover:scale-105 transition">
          Accessories
        </div>
      </div>
    </section>

      <section className="px-10 py-16 bg-gray-50">
        <h2 className="text-4xl font-bold text-center mb-12">
          Featured Products
        </h2>

        <div className="flex justify-center mb-10">
          <input
            type="text"
            placeholder="AI Smart Search Products..."
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
            className="w-full md:w-[500px] p-4 rounded-xl border shadow-lg"
          />
        </div>

        <div className="grid md:grid-cols-3 gap-10">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product._id}
              id={product._id}
              title={product.title}
              price={product.price}
              image={product.image}
            />
          ))}
        </div>
      </section>

      <section className="px-10 py-20 bg-white text-center">
        <h2 className="text-4xl font-bold">
          AI Recommendations
        </h2>

        <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
          Smart AI-powered personalized product
          recommendations for customers.
        </p>
      </section>
    </div>
  );
}

export default Home;