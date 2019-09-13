/* eslint-disable no-script-url */
import React from 'react';
import axios from 'axios'
import Schedules from './Schedules'
import Active from './ActiveFlows'
import Paper from "@material-ui/core/Paper";


class Dashboard extends React.Component
{
    constructor(props)
    {
        super(props);
        this.state = {
            rows: []
        }
    }

    componentDidMount()
    {
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
            <div>
                <Paper className={this.props.style.paper}>
                    <Active/>
                </Paper>
                <br/>
                <Paper className={this.props.style.paper}>
                    <Schedules/>
                </Paper>
            </div>
        )}
}

export default Dashboard
