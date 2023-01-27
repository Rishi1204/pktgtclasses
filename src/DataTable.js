import { useMemo, useState } from 'react';
import { useTable } from 'react-table';
// import DATA from "./Scholastics_Responses.json"
import DATA from './Scholastics_S23.json';
import { COLUMNS } from './columns';
import './table.css';

// test commit
const DataTable = () => {
	const columns = useMemo(() => COLUMNS, []);
	let data = useMemo(() => DATA, []);

	const [searchTerm, setSearchTerm] = useState('');

	if (!(searchTerm === '')) {
		let search = searchTerm;
		search = search.replace(/ /g, '');
		data = data.filter(
			(course) =>
				course.Course_Name.toLowerCase().indexOf(search.toLowerCase()) !== -1
		);
	}

	const tableInstance = useTable({
		columns,
		data,
	});

	const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
		tableInstance;

	return (
		<div>
			<div>
				<input
					type="text"
					placeholder="Search Course Name..."
					style={{ width: '500px', textAlign: 'center' }}
					onChange={(event) => {
						setSearchTerm(event.target.value);
					}}
				/>
			</div>
			<div className="Table">
				<table {...getTableProps}>
					<thead>
						{headerGroups.map((headerGroup) => (
							<tr {...headerGroup.getHeaderGroupProps()}>
								{headerGroup.headers.map((column) => (
									<th {...column.getHeaderProps()}>
										{column.render('Header')}
									</th>
								))}
							</tr>
						))}
					</thead>
					<tbody {...getTableBodyProps}>
						{rows.map((row) => {
							prepareRow(row);
							return (
								<tr {...row.getRowProps()}>
									{row.cells.map((cell) => (
										<td {...cell.getCellProps()}>{cell.render('Cell')}</td>
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
