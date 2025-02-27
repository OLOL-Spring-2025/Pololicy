import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000'; // change based on where you host back

export const fetchData = async() => {
    try {
        const response = await axios.get(`${API_BASE_URL}/api/data`);
        return response.data;
    } catch (error) {
        console.error("ERROR FETCHING DATA: ", error);
        throw error;
    }
}

export const submitData = async(data) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/data`);
        return response.data;
    } catch (error) {
        console.error("ERROR SUBMITTING DATA: ", error);
        throw error;
    }
}