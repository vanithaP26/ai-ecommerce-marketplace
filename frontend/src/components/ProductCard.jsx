import { Link } from "react-router-dom";

function ProductCard({
  title,
  price,
  image,
  id,
}) {
  return (
    <div className="bg-white shadow-lg rounded-xl overflow-hidden hover:scale-105 transition duration-300">
      <img
        src={image}
        alt={title}
        className="h-60 w-full object-cover"
      />

      <div className="p-4">
        <h2 className="text-xl font-semibold">
          {title}
        </h2>

        <p className="text-blue-600 font-bold mt-2">
          ₹{price}
        </p>

        <Link to={`/product/${id}`}>
          <button className="mt-4 w-full bg-black text-white py-2 rounded-lg hover:bg-gray-800">
            View Product
          </button>
        </Link>
      </div>
    </div>
  );
}

export default ProductCard;