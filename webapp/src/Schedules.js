/* eslint-disable no-script-url */
import React from 'react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';
import axios from 'axios'
import { Link } from "react-router-dom";


class Schedules extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            rows: []
        }
    }

    componentDidMount() {
        let auth = {
            username: localStorage.getItem('username'),
            password: localStorage.getItem('password')
        };
        axios.get(process.env.REACT_APP_API_URL+'/api/schedules', {auth: auth}).then(result => {
            this.setState({'rows': result.data});
        });
    }

    render()
    {
        return (
            <React.Fragment>
                <Title>Schedules</Title>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Run At</TableCell>
                            <TableCell>Name</TableCell>
                            <TableCell>Originated File</TableCell>
                            <TableCell>Created At</TableCell>
                            <TableCell>Updated At</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {this.state.rows.map(row => (
                            <TableRow key={row.id}>
                                <TableCell>{row.run_at}</TableCell>
                                <TableCell><Link to={"/flows/"+row.name}>{row.name}</Link></TableCell>
                                <TableCell>{row.originated_file}</TableCell>
                                <TableCell>{row.created_at}</TableCell>
                                <TableCell>{row.updated_at}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </React.Fragment>
        );
    }
}

export default Schedules
