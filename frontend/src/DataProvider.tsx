import { fetchUtils } from 'react-admin';
import { stringify } from 'query-string';

export const apiUrl = process.env.REACT_APP_BACKEND_API_URL;
export const httpClient = (url, options: any = {}) => {
    if (!options.headers) {
        options.headers = new Headers({ Accept: 'application/json' });
    }
    const token = localStorage.getItem('token');
    options.headers.set('Authorization', `Bearer ${token}`);
    return fetchUtils.fetchJson(url, options);
};

export default {
    getList: (resource, params) => {
        const { page = 0, perPage = 0 } = params.pagination;
        const { field, order } = params.sort;
        const query = {
            sort: JSON.stringify([field, order]),
            skip: JSON.stringify((page - 1) * perPage),
            limit: perPage,
            filter: JSON.stringify(params.filter),
        };
        const url = `${apiUrl}/${resource}/?${stringify(query)}`;
        return httpClient(url).then(({ headers, json }) => {
            let total = 0;
            if (headers !== null && headers.has('x-content-range')) {
                const XContentRange = (headers.get('x-content-range') || '/').split('/').pop() || ''
                total = parseInt(XContentRange, 10)
            } else {
                total = json.length
            }
            return ({
                data: json,
                total: total
            })
        });
    },

    getListUnpaginated: (resource, params) => {
        const { field, order } = params.sort;
        const query = {
            sort: JSON.stringify([field, order]),
            filter: JSON.stringify(params.filter),
            limit: JSON.stringify(params.limit),
        };
        const url = `${apiUrl}/${resource}/?${stringify(query)}`;
        return httpClient(url).then(({ json }) => ({ data: json, total: json.length }));
    },

    getOne: (resource, params) =>
        httpClient(`${apiUrl}/${resource}/${params.id}`).then(({ json }) => ({
            data: json,
        })),

    getMany: (resource, params) => {
        const query = {
            filter: JSON.stringify({ id: params.ids }),
        };
        const url = `${apiUrl}/${resource}/?${stringify(query)}`;
        return httpClient(url).then(({ json }) => ({ data: json }));
    },

    getManyReference: (resource, params) => {
        const { page, perPage } = params.pagination;
        const { field, order } = params.sort;
        const query = {
            sort: JSON.stringify([field, order]),
            range: JSON.stringify([(page - 1) * perPage, page * perPage - 1]),
            filter: JSON.stringify({
                ...params.filter,
                [params.target]: params.id,
            }),
        };
        const url = `${apiUrl}/${resource}/?${stringify(query)}`;
        return httpClient(url).then(({ headers, json }) => {
            let total = 10;
            if (headers !== null) {
                const XContentRange = (headers.get('x-content-range') || '/').split('/').pop() || ''
                total = parseInt(XContentRange, 10)
            }
            return ({
                data: json,
                total: total
            })
        });
    },

    update: (resource, params) => 
        httpClient(`${apiUrl}/${resource}/${params.id}`, {
            method: 'PUT',
            body: JSON.stringify(params.data),
        }).then(({ json }) => ({ data: json }))
    ,

    updateMany: (resource, params) => {
        const query = {
            filter: JSON.stringify({ id: params.ids}),
        };
        return httpClient(`${apiUrl}/${resource}/?${stringify(query)}`, {
            method: 'PUT',
            body: JSON.stringify(params.data),
        }).then(({ json }) => ({ data: json }));
    },

    create: (resource, params) => {
        return httpClient(`${apiUrl}/${resource}/`, {
            method: 'POST',
            body: JSON.stringify(params.data),
        }).then(({ json }) => ({
            data: { ...params.data, id: json.id },
        })).catch((e)=>{
            return Promise.reject(e);
        });
    },

    delete: (resource, params) =>
        httpClient(`${apiUrl}/${resource}/${params.id}`, {
            method: 'DELETE',
        }).then(({ json }) => ({ data: json })),

    deleteMany: (resource, params) => {
        const query = {
            filter: JSON.stringify({ id: params.ids}),
        };
        return httpClient(`${apiUrl}/${resource}/?${stringify(query)}`, {
            method: 'DELETE',
            body: JSON.stringify(params.data),
        }).then(({ json }) => ({ data: json }));
    }
};
