import {
  Pencil,
  Trash2,
  Search,
} from "lucide-react";

function Table({
  products,
  deleteProduct,
}) {
  return (
    <div className="bg-white p-8 rounded-2xl shadow">

      {/* HEADER */}

      <div className="flex justify-between items-center mb-8">

        <div>
          <h2 className="text-3xl font-bold">
            Product Inventory
          </h2>

          <p className="text-gray-500 mt-1">
            Manage your products
          </p>
        </div>

        {/* SEARCH */}

        <div className="flex items-center bg-gray-100 px-4 py-3 rounded-xl w-[300px]">

          <Search
            size={20}
            className="text-gray-500"
          />

          <input
            type="text"
            placeholder="Search product..."
            className="bg-transparent outline-none ml-3 w-full"
          />

        </div>
      </div>

      {/* TABLE */}

      <div className="overflow-x-auto">

        <table className="w-full">

          <thead>
            <tr className="border-b text-gray-500">

              <th className="text-left py-4">
                Product
              </th>

              <th className="text-left py-4">
                Category
              </th>

              <th className="text-left py-4">
                Price
              </th>

              <th className="text-left py-4">
                Stock
              </th>

              <th className="text-left py-4">
                Status
              </th>

              <th className="text-left py-4">
                Actions
              </th>

            </tr>
          </thead>

          <tbody>

            {products.map((product) => (

              <tr
                key={product._id}
                className="border-b hover:bg-gray-50 transition"
              >

                {/* PRODUCT */}

                <td className="py-5">

                  <div className="flex items-center gap-4">

                    <img
                      src={product.image}
                      alt={product.title}
                      className="w-16 h-16 rounded-xl object-cover"
                    />

                    <div>

                      <h3 className="font-semibold text-lg">
                        {product.title}
                      </h3>

                      <p className="text-gray-500 text-sm">
                        {product.description}
                      </p>

                    </div>

                  </div>

                </td>

                {/* CATEGORY */}

                <td>
                  {product.category}
                </td>

                {/* PRICE */}

                <td className="font-semibold">
                  ₹{product.price}
                </td>

                {/* STOCK */}

                <td>
                  {product.stock}
                </td>

                {/* STATUS */}

                <td>

                  {product.stock > 0 ? (

                    <span className="bg-green-100 text-green-600 px-4 py-2 rounded-full text-sm">
                      In Stock
                    </span>

                  ) : (

                    <span className="bg-red-100 text-red-600 px-4 py-2 rounded-full text-sm">
                      Out of Stock
                    </span>

                  )}

                </td>

                {/* ACTIONS */}

                <td>

                  <div className="flex gap-4">

                    {/* EDIT */}

                    <button
                      onClick={() =>
                        (window.location.href =
                          `/seller/edit/${product._id}`)
                      }
                      className="bg-blue-100 p-3 rounded-lg hover:bg-blue-200 transition"
                    >

                      <Pencil
                        size={18}
                        className="text-blue-600"
                      />

                    </button>

                    {/* DELETE */}

                    <button
                      onClick={() =>
                        deleteProduct(
                          product._id
                        )
                      }
                      className="bg-red-100 p-3 rounded-lg hover:bg-red-200 transition"
                    >

                      <Trash2
                        size={18}
                        className="text-red-600"
                      />

                    </button>

                  </div>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>
  );
}

export default Table;