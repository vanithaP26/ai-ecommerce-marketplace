import { Link } from "react-router-dom";

function ProductCard({
  title,
  price,
  image,
  id,
}) {
  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl hover:-translate-y-2 transition duration-300">
      <div className="relative">
        <img
          src={image}
          alt={title}
          className="h-72 w-full object-cover"
        />

        <span className="absolute top-4 left-4 bg-red-500 text-white px-4 py-1 rounded-full text-sm">
          Trending
        </span>
      </div>

      <div className="p-5">
        <h2 className="text-2xl font-bold">
          {title}
        </h2>

        <div className="flex items-center gap-1 mt-2 text-yellow-500">
          ⭐⭐⭐⭐⭐
        </div>

        <p className="text-blue-600 text-2xl font-bold mt-3">
          ₹{price}
        </p>

        <Link to={`/product/${id}`}>
          <button className="mt-5 w-full bg-black text-white py-3 rounded-xl hover:bg-gray-800 transition">
            View Product
          </button>
        </Link>
      </div>
    </div>
  );
}

export default ProductCard;