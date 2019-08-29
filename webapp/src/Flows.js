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


class Flows extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            schedule_name: props.match.params.schedule_name,
            rows: []
        }
    }

    componentDidMount() {
        axios.get('http://127.0.0.1:5000/api/flows/'+this.state.schedule_name).then(result => {
            this.setState({'rows': result.data});
        });
    }

    render()
    {
        return (
            <React.Fragment>
                <Title>Flows</Title>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Status</TableCell>
                            <TableCell>Name</TableCell>
                            <TableCell>Created At</TableCell>
                            <TableCell>Updated At</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {this.state.rows.map(row => (
                            <TableRow key={row.id}>
                                <TableCell>{row.status}</TableCell>
                                <TableCell><Link to={{pathname: "/tasks/"+row.id, flow: row}}>{row.name}</Link></TableCell>
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

export default Flows
