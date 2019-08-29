/* eslint-disable no-script-url */
import React from 'react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';
import axios from 'axios'


class Flows extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            flow: props.location.flow,
            flow_id: props.match.params.flow_id,
            rows: []
        }
    }

    componentDidMount() {
        axios.get('http://127.0.0.1:5000/api/tasks/'+this.state.flow_id).then(result => {
            this.setState({'rows': result.data});
        });
    }

    render()
    {
        return (
            <React.Fragment>
                <Title>Task</Title>

                <Table size="small">
                    <TableHead>
                        <TableRow>
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
        );
    }
}

export default Flows
