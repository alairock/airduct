/* eslint-disable no-script-url */
import React from 'react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';
import axios from 'axios'
import Paper from "@material-ui/core/Paper";


class Flows extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            flow: props.location.flow,
            flow_id: props.match.params.flow_id,
            rows: [],
            keep_checking: true
        }
    }

    checkStatus() {
        let auth = {
            username: localStorage.getItem('username'),
            password: localStorage.getItem('password')
        };
        axios.get(process.env.REACT_APP_API_URL+'/api/tasks/'+this.state.flow_id, {auth: auth}).then(result => {
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
            <Paper className={this.props.style.paper}>
            <React.Fragment>
                <Title>Task</Title>

                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>id</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Step</TableCell>
                            <TableCell>Completed At</TableCell>
                            <TableCell>Created At</TableCell>
                            <TableCell>Updated At</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {this.state.rows.map(row => (
                            <TableRow key={row.id}>
                                <TableCell>{row.id}</TableCell>
                                <TableCell>{row.status}</TableCell>
                                <TableCell>{row.step}</TableCell>
                                <TableCell>{row.completed_at}</TableCell>
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
