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
import Paper from "@material-ui/core/Paper";


class Flows extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            schedule_name: props.match.params.schedule_name,
            rows: []
        }
    }

    componentDidMount() {
        let auth = {
            username: localStorage.getItem('username'),
            password: localStorage.getItem('password')
        };
        axios.get(process.env.REACT_APP_API_URL+'/api/flows/'+this.state.schedule_name, {auth: auth}).then(result => {
            this.setState({'rows': result.data});
        });
    }

    render()
    {
        return (
            <Paper className={this.props.style.paper}>
            <React.Fragment>
                <Title>Flows - {this.state.schedule_name}</Title>
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
                                <TableCell><Link to={"/tasks/"+row.id}>{row.status}</Link></TableCell>
                                <TableCell>{row.name}</TableCell>
                                <TableCell>{row.created_at}</TableCell>
                                <TableCell>{row.updated_at}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </React.Fragment>
            </Paper>
        );
    }
}

export default Flows
