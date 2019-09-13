import React from "react";
import axios from "axios";
import Title from "./Title";
import Table from "@material-ui/core/Table";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import TableCell from "@material-ui/core/TableCell";
import TableBody from "@material-ui/core/TableBody";
import {Link} from "react-router-dom";

class Active extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            rows: [],
            keep_checking: true
        }
    }

    checkStatus() {
        let auth = {
            username: localStorage.getItem('username'),
            password: localStorage.getItem('password')
        };
        axios.get(process.env.REACT_APP_API_URL+'/api/flows', {auth: auth}).then(result => {
            let keep_checking = false;
            for(let i = 0; i < result.data.length; i++) {
                if (result.data[i].status !== 'Complete' ) {

                    keep_checking = true
                }
            }
            this.setState({'rows': result.data, 'keep_checking': keep_checking});
            if (keep_checking === false) {
                clearInterval(this.interval);
            }
        });
    }

    componentDidMount() {
        this.checkStatus();
        if (this.state.keep_checking === true){
            this.interval = setInterval(() => this.checkStatus(), 5000);
        }
    }

    componentWillUnmount() {
        clearInterval(this.interval);
    }

    render()
    {
        return (
                <React.Fragment>
                    <Title>Active/Recent Flows</Title>
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
                                    <TableCell><Link to={"/flows/"+row.name}>{row.name}</Link></TableCell>
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


export default Active
