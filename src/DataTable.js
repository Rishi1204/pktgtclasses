import { useMemo, useState } from 'react';
import { useTable } from 'react-table';
import DATA from './data/new_classes_added.json';
import { COLUMNS } from './columns';
import './table.css';

const transformTakersToStrings = (data) => {
  // Iterate over each course in the data
  data.forEach(course => {
    // Convert Current_Takers array to a comma-separated string
    if (Array.isArray(course.Current_Takers)) {
      course.Current_Takers = course.Current_Takers.join(', ');
    }

    // Convert Past_Takers array to a comma-separated string
    if (Array.isArray(course.Past_Takers)) {
      course.Past_Takers = course.Past_Takers.join(', ');
    }
  });

  return data;
};



const DataTable = () => {
  const [searchTerm, setSearchTerm] = useState('');

  // Memoizing the columns and filtered data for better performance
  const columns = useMemo(() => COLUMNS, []);
  

  const updatedData = transformTakersToStrings(DATA);
  
  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) {
      return DATA; // Return full data if search term is empty
    }

	console.log(DATA);


    const search = searchTerm.toLowerCase();
    return DATA.filter(course => 
      course.Course_Name.toLowerCase().includes(search)
    );
  }, [searchTerm]);

  // Create table instance using the filtered data
  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } = useTable({
    columns,
    data: filteredData,
  });

  return (
    <div>
      <div>
        <input
          type="text"
          placeholder="Search Course Name..."
          style={{ width: '500px', textAlign: 'center' }}
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
        />
      </div>
      
      <div className="Table">
        <table {...getTableProps()}>
          <thead>
            {headerGroups.map(headerGroup => (
              <tr {...headerGroup.getHeaderGroupProps()} key={headerGroup.id}>
                {headerGroup.headers.map(column => (
                  <th {...column.getHeaderProps()} key={column.id}>
                    {column.render('Header')}
                  </th>
                ))}
              </tr>
            ))}
          </thead>

          <tbody {...getTableBodyProps()}>
            {rows.map(row => {
              prepareRow(row);
              return (
                <tr {...row.getRowProps()} key={row.id}>
                  {row.cells.map(cell => (
                    <td {...cell.getCellProps()} key={cell.column.id}>
                      {cell.render('Cell')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;
