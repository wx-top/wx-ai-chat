import {http} from '../utils/http.js'

export const addRepository = async (data) => {
    return await http.post('/repository/repositories', data)
}

export const getRepositories = async (keyword = '') => {
    const params = keyword ? { keyword } : {}
    return await http.get('/repository/repositories', params)
}

// 获取知识库文件列表
export const getRepositoryFilesById = async (id) => {
    return await http.get(`/repository/repositories/${id}/files`)
}

// 上传文件到知识库
export const uploadFile = async (repositoryId, file, name) => {
    return await http.upload(`/repository/repositories/${repositoryId}/files?name=${name}`, file.path)
}

// 删除知识库文件
export const deleteFile = async (repositoryId, fileId) => {
    return await http.delete(`/repository/repositories/${repositoryId}/files/${fileId}`)
}

// 更新知识库
export const updateRepository = async (id, data) => {
    return await http.put(`/repository/repositories/${id}`, data)
}

// 删除知识库
export const deleteRepository = async (id) => {
    return await http.delete(`/repository/repositories/${id}`)
}